import tkinter as tk


# Tab page where show input fields.
# Add the data in the fields to the database when the Add button is clicked.
class AddTab:
    def __init__(self, panel):
        self.panel = panel
        self.tab = panel.make_tab('Add a car')
        # Make a dictionary with pairs of attribute and StringVar.
        # It is used to contain the input data.
        self.car_data_fields = panel.make_car_data_fields()

        # Arrange the input fields in the tab page.
        panel.make_input_frame(self.tab, self.car_data_fields)

        submit_button = tk.Button(self.tab, text='Add',
                                  command=lambda: self.add_car()
                                  )
        # Place the button at the bottom of the tab page.
        submit_button.pack(anchor=tk.S)
        self.logger = panel.logger

    # Return new id which is assigned to new data to be added.
    def new_id(self):
        # Retrieve all data from the database
        cars = self.panel.db.get_cars_list()

        # Find the smallest id which isn't assigned to any rows.
        ids = (car['id'] for car in cars)
        num = 1
        for id in ids:
            # rows are sorted by id
            if id != num:
                # This num isn't assigned to a row
                break
            num += 1

        self.logger.debug('id to be assigned: %d', num)
        return str(num)

    # Insert the data which is entered in the Add tab to database
    def add_car(self):
        # Convert StringVar to string in the input fields
        car_data = self.panel.field_data_to_dict(self.car_data_fields)
        car_data['id'] = self.new_id()
        self.logger.debug('add car data: %s', car_data)

        # Give the data to the database function to add the data
        self.panel.submit_request(car_data,
                                  self.panel.db.add_new_car)
