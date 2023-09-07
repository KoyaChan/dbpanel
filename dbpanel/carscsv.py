import csv
# if __name__ == '__main__':
from carsdb import CarsDB
from carsdb import Car
from carsdb import CarDataAccessor
from carsdb import ServerNotReadyError
# else:
#     from .carsdb import CarsDB
#     from .carsdb import CarDataAccessor
#     from .carsdb import ServerNotReadyError


class CarsCSV(CarDataAccessor):
    FILENAME = 'cars.csv'

    def __init__(self):
        self.filename = CarsCSV.FILENAME
        self._header = None

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
                for car in cars:
                    writer.writerow(car)

            return True

        except OSError as e:
            print('Create csv file failed. error: ', e.strerror)
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
        print(f'Failed to get header as no rows in {self.filename}.')
        return None

    # Get cars list from the csv file, and return list of dictionaries.
    # If failed, return None.
    def get_cars_list(self) -> list:
        try:
            with open(self.filename, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=',')
                return list(reader)

        except OSError as e:
            print(f'Get cars from {self.filename} failed. error: ', e.strerror)
            return None

    # Add car data to the csv file.
    # Return True if succeeded else False.
    def add_new_car(self, car_data: dict) -> bool:
        try:
            with open(self.filename, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, delimiter=',',
                                        fieldnames=self.header,
                                        quoting=csv.QUOTE_MINIMAL)
                writer.writerow(car_data)

            return True

        except OSError as e:
            print(f'Add a car to {self.filename} failed. error: ', e.strerror)
            return False

    # Delete a car data from the csv file.
    # Return True if succeeded, else False.
    def delete_a_car(self, car_data: dict) -> bool:
        cars_list = self.get_cars_list()

        # find the car with the same id as car_data in the list
        car_found = next((car for car in cars_list if str(car_data['id'])
                          == str(car['id'])),
                         None)

        if car_found is None:
            print(f'{car_data} is not found')
            return False

        cars_list.remove(car_found)
        return self.create(cars_list)

    # Retrieve a car data with the specified car data from the csv file.
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
        pass


# Create the csv file with the data got from the cars.json.
def main():
    try:
        cars_db = CarsDB()

    except ServerNotReadyError:
        print('Server is not ready')
        exit(1)

    else:
        cars_csv = CarsCSV()
        cars_csv.create(cars_db.get_cars_list())


if __name__ == '__main__':
    main()
