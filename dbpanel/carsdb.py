import requests
import json

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


class CarsDB:
    h_close = {'Connection': 'Close'}
    h_content = {'Content-Type': 'application/json'}

    def __init__(self, url='http://localhost', port=3000):
        self.server_url = url + ':' + str(port)
        if not self.check_server():
            raise ServerNotReadyError()

    def request_url(self):
        return self.server_url + '/cars'

    def check_server(self, cid=None):
        # return True if the server returns ok(200) else False
        try:
            reply = requests.head(self.server_url, headers=CarsDB.h_close)

        except requests.RequestException as e:
            print('Communication error: ', e.response)
            return False

        else:
            if reply.status_code == requests.codes.ok:
                return True
            else:
                print('Server error: ', reply.status_code)
                return False

    def get_cars_list(self):
        # get cars list from json-server, and return dict type data
        # if failed, return None
        try:
            target_url = self.request_url() + '/?_sort=id&_order=asc'
            reply = requests.get(target_url,
                                 headers=CarsDB.h_close)

        except requests.RequestException as e:
            print('Get request error: ', e.response)
            return None

        else:
            if reply.status_code == requests.codes.ok:
                # convert json object to dict and return it
                return reply.json()
            elif reply.status_code == requests.codes.not_found:
                print('Resource not found')
                return None
            else:
                print('Get request error, status code: ', reply.status_code)
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
            print('Post request error: ', e.response)
            return False

        else:
            if reply.status_code == requests.codes.created:
                return True
            else:
                print('Post request status code: ', reply.status_code)
                return False

    def delete_a_car(self, car_data: dict) -> bool:
        target_url = self.request_url() + '/' + str(car_data['id'])
        print('target_url: ', target_url)
        try:
            reply = requests.delete(target_url)

        except requests.RequestException as e:
            print('Delete request error: ', e.response)
            return False

        else:
            print('Delete request status code: ', reply.status_code)
            return True

    def select_a_car(self, car_data: dict) -> dict:
        target_url = self.request_url() + '/?id=' + str(car_data['id'])
        try:
            reply = requests.get(target_url)

        except requests.RequestException as e:
            print('Get request error: ', e.response)
            return False

        else:
            print('Get request status code: ', + reply.status_code)
            return reply.json()[0]  # reply.json() is a list

    def update_a_car(self, car_data: dict) -> bool:
        target_url = self.request_url() + '/' + str(car_data['id'])
        try:
            reply = requests.put(target_url,
                                 headers=CarsDB.h_content,
                                 data=json.dumps(car_data))

        except requests.RequestException as e:
            print('Put request error: ', e.response)
            return False

        else:
            if reply.status_code == requests.codes.ok:
                return True
            else:
                print('Put request status code: ', reply.status_code)


if __name__ == '__main__':
    cars_db = CarsDB()
    print(cars_db.get_cars_list())
