import requests
import json
import logging
from abc import ABC, abstractmethod

# http status codes
# https://requests.readthedocs.io/en/latest/api/#status-code-lookup


class ServerNotReadyError(Exception):
    pass


class ValidationError(Exception):
    pass


class Car:
    def __init__(self, car_attr_value: dict):
        self.id = self.validate_id(car_attr_value['id'])
        self.brand = self.validate_brand(car_attr_value['brand'])
        self.model = self.validate_model(car_attr_value['model'])
        self.production_year = self.validate_year(
                                    car_attr_value['production_year']
                                    )
        self.convertible = self.validate_convertible(
                                    car_attr_value['convertible']
                                    )

    def validate_id(self, id:str):
        if id.isdigit():
            return int(id)
        else:
            raise ValidationError()

    def validate_brand(self, brand: str):
        return brand

    def validate_model(self, model: str):
        return model

    def validate_year(self, year: str):
        if year.isdigit():
            if 1940 <= int(year) <= 2030:
                return int(year)
            else:
                raise ValidationError()

    def validate_convertible(self, convertible: str):
        if convertible.upper() == 'YES' or convertible.upper() == 'TRUE':
            return True
        elif convertible.upper() == 'NO' or convertible.upper() == 'FALSE':
            return False
        else:
            raise ValidationError


# Abstract class to define CRUD functions
class CarDataAccessor(ABC):

    # Get cars list from json-server, and return list of dictionaries.
    # If failed, return None.
    @abstractmethod
    def get_cars_list(self) -> list:
        pass

    # Add car data to the json db.
    # Return True if succeeded else False.
    @abstractmethod
    def add_new_car(self, car_data: dict) -> bool:
        pass

    # Delete a car data.
    # Return True if succeeded else False.
    @abstractmethod
    def delete_a_car(self, car_data: dict) -> bool:
        pass

    # Return a car data retrieved from the given car_data.
    # Return None if not found.
    @abstractmethod
    def select_a_car(self, car_data: dict) -> dict:
        pass


class CarsDB(CarDataAccessor):
    LOG_FORMAT = '%(asctime)s:%(name)s:%(levelname)s:%(message)s'
    h_close = {'Connection': 'Close'}
    h_content = {'Content-Type': 'application/json'}

    def __init__(self, url='http://localhost', port=3000):
        self.logger = self.logging_setup()
        self.server_url = url + ':' + str(port)
        if not self.check_server():
            raise ServerNotReadyError()

    def logging_setup(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        # handler = logging.FileHandler('dbpanel.log', 'a')
        formatter = logging.Formatter(self.LOG_FORMAT)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def log_info(self, message, *args):
        if len(args):
            self.logger.info(message, args)
        else:
            self.logger.info(message)

    def log_debug(self, message, *args):
        if len(args):
            self.logger.debug(message, args)
        else:
            self.logger.debug(message)

    def log_error(self, message, *args):
        if len(args):
            self.logger.error(message, args)
        else:
            self.logger.error(message)

    def request_url(self):
        return self.server_url + '/cars'

    def check_server(self, cid=None):
        # return True if the server returns ok(200) else False
        try:
            reply = requests.head(self.server_url, headers=CarsDB.h_close)

        except requests.RequestException as e:
            self.log_error('Communication error: %s', e.response)
            return False

        else:
            if reply.status_code == requests.codes.ok:
                return True
            else:
                self.log_error('Server error: %s', reply.status_code)
                return False

    def get_cars_list(self):
        # get cars list from json-server, and return list of dictionaries.
        # if failed, return None
        try:
            target_url = self.request_url() + '/?_sort=id&_order=asc'
            reply = requests.get(target_url,
                                 headers=CarsDB.h_close)

        except requests.RequestException as e:
            self.log_error('Get request error: %s', e.response)
            return None

        else:
            if reply.status_code == requests.codes.ok:
                # convert json object to list of dict and return it
                return reply.json()
            elif reply.status_code == requests.codes.not_found:
                self.log_error('Resource not found')
                return None
            else:
                self.log_error('Get request error, status code: %d', reply.status_code)
                return None

    def add_new_car(self, car_data: dict) -> bool:
        # add car data to the json db
        # return True if succeeded else False
        try:
            # convert car data to json and give it to the json server
            reply = requests.post(self.request_url(),
                                  headers=CarsDB.h_content,
                                  data=json.dumps(car_data))

        except requests.RequestException as e:
            self.log_error('Post request error: %s', e.response)
            return False

        else:
            if reply.status_code == requests.codes.created:
                return True
            else:
                self.log_error('Post request status code: %d', reply.status_code)
                return False

    def delete_a_car(self, car_data: dict) -> bool:
        target_url = self.request_url() + '/' + str(car_data['id'])
        self.logger.info('target_url: %s', target_url)
        try:
            reply = requests.delete(target_url)

        except requests.RequestException as e:
            self.log_error('Delete request error: %s', e.response)
            return False

        else:
            self.logger.info('Delete request status code: %d', reply.status_code)
            return True

    def select_a_car(self, car_data: dict) -> dict:
        target_url = self.request_url() + '/?id=' + str(car_data['id'])
        try:
            reply = requests.get(target_url)

        except requests.RequestException as e:
            self.log_error('Get request error: %s', e.response)
            return None

        else:
            self.logger.info('Get request status code: %d', reply.status_code)
            return reply.json()[0]  # reply.json() is a list

    def update_a_car(self, car_data: dict) -> bool:
        target_url = self.request_url() + '/' + str(car_data['id'])
        try:
            reply = requests.put(target_url,
                                 headers=CarsDB.h_content,
                                 data=json.dumps(car_data))

        except requests.RequestException as e:
            self.log_error('Put request error: %s', e.response)
            return False

        else:
            if reply.status_code == requests.codes.ok:
                return True
            else:
                self.logger.info('Put request status code: %d', reply.status_code)


if __name__ == '__main__':
    try:
        cars_db = CarsDB()
    except ServerNotReadyError:
        print('Sever Not Ready')
        exit(1)

    print(cars_db.get_cars_list())
