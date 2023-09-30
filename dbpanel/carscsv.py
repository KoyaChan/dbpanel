import csv
if __name__ == '__main__' or __name__ == 'carscsv':
    from carsdb import CarsDB
    from carsdb import Car
    from carsdb import CarDataAccessor
    from carsdb import ServerNotReadyError
    from logger import Logger
else:
    from .carsdb import CarsDB
    from .carsdb import Car
    from .carsdb import CarDataAccessor
    from .carsdb import ServerNotReadyError
    from .logger import Logger


class CarsCSV(CarDataAccessor):
    FILENAME = 'cars.csv'

    def __init__(self):
        self.filename = CarsCSV.FILENAME
        self._header = None
        self.logger = Logger(__name__).get_logger()

    # Newly create the csv file with the data given in cars parameter.
    # Return True if succeeded else False.
    def create(self, cars: list) -> bool:
        # cars contains a list of dictionary
        header = cars[0].keys()
        try:
            with open(self.filename, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile,
                                        fieldnames=header,
                                        quoting=csv.QUOTE_MINIMAL)
                writer.writeheader()
                for car in sorted(cars, key=lambda car: int(car['id'])):
                    writer.writerow(car)

            return True

        except OSError as e:
            self.logger.error('Create csv file failed. error: %s', e.strerror)
            return False

    @property
    # Return the header row from the csv file.
    def header(self) -> list:
        if self._header is not None:
            return self._header

        with open(self.filename, 'r', newline='') as csvfile:
            for row in csv.reader(csvfile, delimiter=','):
                # need only the first row
                self._header = row
                return self._header

        # The csv file doesn't have any rows.
        self.logger.error('Failed to get header as no rows in %s',
                          self.filename)
        return None

    # Get cars list from the csv file, and return list of dictionaries.
    # If failed, return None.
    def get_cars_list(self) -> list:
        try:
            with open(self.filename, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=',')
                return list(reader)

        except OSError as e:
            self.logger.error('Get cars from %s failed. error: %s',
                              self.filename, e.strerror)
            return None

    # Add car data to the csv file.
    # Return True if succeeded else False.
    def add_new_car(self, car_data: dict) -> bool:
        cars = self.get_cars_list()
        if cars is None:
            return False

        cars.append(car_data)
        if not self.create(cars):
            return False

        self.logger.info('Car id: %s added', str(car_data['id']))
        return True

    # Delete a car data from the csv file.
    # Return True if succeeded, else False.
    def delete_a_car(self, car_data: dict) -> bool:
        cars_list = self.get_cars_list()

        # find the car with the same id as car_data in the list
        car_found = next((car for car in cars_list if str(car_data['id'])
                          == str(car['id'])),
                         None)

        if car_found is None:
            self.logger.error('car id: %s not found', str(car_data['id']))
            return False

        cars_list.remove(car_found)
        return self.create(cars_list)

    # Retrieve a car data with the id of specified car data.
    # Return None if not found else the dict type data of the car.
    def select_a_car(self, car_data: dict) -> dict:
        cars_list = self.get_cars_list()

        # return the car which matches the specified car_data by its id
        car_found = next(
            (car for car in cars_list if car['id'] == car_data['id']),
            None
            )

        return None if car_found is None else Car(car_found).__dict__

    # Update a car data in the csv file.
    # Return True if suceeded, else False.
    def update_a_car(self, car_data: dict) -> bool:
        # delete the car data which has the same id as th specified data
        if not self.delete_a_car(car_data):
            self.logger.error('car id %s not found', str(car_data['id']))
            return False

        if not self.add_new_car(car_data):
            self.logger.error('failed to add a car, id: %s', str(car_data['id']))
            return False

        self.logger.info('update success id: %s', str(car_data['id']))
        return True


# Create the csv file with the data got from the cars.json.
def main():
    try:
        cars_db = CarsDB()

    except ServerNotReadyError:
        Logger(__name__).get_logger().error('Server is not ready')
        exit(1)

    else:
        cars_csv = CarsCSV()
        cars_csv.create(cars_db.get_cars_list())


if __name__ == '__main__':
    main()
