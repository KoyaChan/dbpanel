import tkinter as tk
from tkinter import ttk
from .carsdb import Car
from .carsdb import CarsDB
from .carsdb import ServerNotReadyError
from .carsdb import ValidationError


# Todo :
# - When user enters an id in DeleteTab or UpdateTab page then its data is retrieved
# - Prevent id field from changed in tab pages
# - Show id value to be assigned to new data in AddTab automatically


# Tab page in the panel where is the data is listed.
# When a row is clicked in the list, its data is read into
# CarsPanel.current_car_data.
class ListTab(tk.Frame):
    def __init__(self, panel):
        self.tab = panel.make_tab('List cars')
        self.car_table = None
        self.panel = panel
        self.list_frame = tk.Frame(self.tab)
        self.list_frame.pack()
        self.list_cars()

    # Show the treeview table on list_frame.
    # The table is filled with the data retrieved from database.
    def list_cars(self):
        # Make the header of table with the keys of dictionary data.
        columns = self.panel.get_car_attributes()
        if self.car_table is None:
            # reference :
            # https://office54.net/python/tkinter/ttk-treeview-table
            #
            # Show headings of the table.
            self.car_table = ttk.Treeview(self.list_frame,
                                          columns=columns,
                                          show='headings'
                                          )
            for column in columns:
                if column == 'id':
                    self.car_table.heading(column, text=column,
                                           anchor=tk.CENTER)
                    self.car_table.column(column, anchor=tk.CENTER, width=50)
                else:
                    self.car_table.heading(column, text=column, anchor=tk.W)
                    self.car_table.column(column, anchor=tk.W, width=150)

            # selected row data is read into CarsPanel.current_car_data .
            self.car_table.bind('<<TreeviewSelect>>',
                                self.panel.fill_current_car_data)
            self.car_table.pack()
        else:
            # Clean up the old data in the table
            self.car_table.delete(*self.car_table.get_children())

        # Retrieve all data from the database
        cars = self.panel.db.get_cars_list()
        cars.sort(key=lambda car: car['id'])

        # Adjust the height of the Treeview with the number of rows
        self.car_table.config(height=len(cars))

        for car in cars:
            # insert the data of a row into the bottm of the table
            self.car_table.insert(parent='',
                                  index='end',
                                  values=tuple(car.values())
                                  )


# Tab page where show input fields.
# Add the data in the fields to the database when the Add button is clicked.
class AddTab:
    def __init__(self, panel):
        self.tab = panel.make_tab('Add a car')
        # Make a dictionary with pairs of attribute and StringVar.
        # It is used to contain the input data.
        self.car_data_fields = panel.make_car_data_fields()

        # Arrange the input fields in the tab page.
        panel.make_input_frame(self.tab, self.car_data_fields)

        self.panel = panel
        submit_button = tk.Button(self.tab, text='Add',
                                  command=lambda: self.add_car()
                                  )
        # Place the button at the bottom of the tab page.
        submit_button.pack(anchor=tk.S)

    # Insert the data which is entered in the Add tab to database
    def add_car(self):
        # Convert StringVar to string in the input fields
        car_data = self.panel.field_data_to_dict(self.car_data_fields)

        # Give the data to the database function to add the data
        self.panel.submit_request(car_data,
                                  self.panel.db.add_new_car)


# Tab page to delete a data which fills the field in this tab page.
# Fields are filled with data which is clicked in the list tab page.
class DeleteTab:
    def __init__(self, panel):
        self.tab = panel.make_tab('Delete a car')
        panel.make_input_frame(self.tab, panel.current_field)
        self.panel = panel
        submit_button = tk.Button(self.tab, text='Delete',
                                  command=self.delete_car
                                  )
        submit_button.pack(anchor=tk.S)

    def delete_car(self):
        # Currently clicked data in the list tab page
        car_to_delete = self.panel.current_car_data

        # Retrieve the data from db by the id of car to delete.
        car_in_db = self.panel.db.select_a_car(car_to_delete)

        # Confirm the car data to delete equals the data in db.
        if (car_in_db == Car(car_to_delete).__dict__):
            # The car data to delete is found in the db.
            self.panel.submit_request(car_to_delete,
                                      self.panel.db.delete_a_car)
        else:
            print("Car to delete isn't found in db")
            print('car in db: ' + str(car_in_db))
            print('car to delete: ' + str(car_to_delete))


# Tab page to change a value in a data.
# Fields are filled with the selected data in the list tab page at first.
# User changes values in the fields in this tab page.
class UpdateTab:
    def __init__(self, panel):
        self.tab = panel.make_tab('Update a car')
        # panel.current_field contains the data selected in the list view
        panel.make_input_frame(self.tab, panel.current_field)
        self.panel = panel
        submit_button = tk.Button(self.tab, text='Update',
                                  command=self.update_car
                                  )
        submit_button.pack(anchor=tk.S)

    def update_car(self):
        # Currently filled data in the update tab page
        car_update_data = self.panel.current_car_data

        self.panel.submit_request(car_update_data,
                                  self.panel.db.update_a_car)


class CarsPanel:
    def __init__(self, cars_db):
        self.db = cars_db
        self.root = tk.Tk()
        self.root.title('Cars DB')
        self.car_attributes = None
        self.notebook = ttk.Notebook(self.root)
        self.__current_car_data = self.make_car_data_fields()
        self.make_tabs()
        self.notebook.pack()
        self.root.mainloop()

    def make_tabs(self):
        self.list_tab = ListTab(self)
        self.add_tab = AddTab(self)
        self.delete_tab = DeleteTab(self)
        self.update_tab = UpdateTab(self)

        # Clear the data in the fields of Add tab page when
        # a tab page is opened.
        self.notebook.bind('<<NotebookTabChanged>>',
                           lambda event:
                           self.clear_car_data(self.add_tab.car_data_fields)
                           )

    def make_tab(self, tab_name):
        tab = tk.Frame(self.notebook)
        self.notebook.add(tab, text=tab_name)
        return tab

    def make_car_data_fields(self):
        # car_data_fields is a dictionary with pairs of car attribute
        # and value.
        car_data_fields = {}
        # attributes is collected from the database
        attributes = self.get_car_attributes()

        for attr in attributes:
            # Each value is StringVar to contain data which is put
            # into Entry widget.
            car_data_fields[attr] = tk.StringVar(self.notebook)

        return car_data_fields

    def make_input_frame(self, tab, car_data_fields):
        # Make a frame with Entry widgets to input values in a tab page.
        # Add tab has its own fields, and other tabs have common fields.
        input_frame = tk.Frame(tab)

        row_num = 0
        for attr in car_data_fields.keys():
            # Arrange each row with "<row name> <Entry widget>" format in grid
            row_num += 1
            label = tk.Label(input_frame, text=attr)
            label.grid(row=row_num, column=1, sticky=tk.W)
            # Show the value when a field has value
            entry = tk.Entry(input_frame,
                             textvariable=car_data_fields[attr]
                             )
            entry.grid(row=row_num, column=2)

        input_frame.pack(anchor=tk.N)

    def get_car_attributes(self):
        # Get a list of dictionary data from database, and return
        # the tuple of keys of the dictionary
        if self.car_attributes is None:
            cars = self.db.get_cars_list()
            self.car_attributes = tuple(cars[0].keys())

        return self.car_attributes

    def fill_current_car_data(self, event):
        # Fill __current_car_data with the data selected in the list tab page.
        # TreeView.focus() returns record_id which points the data clicked
        # in the TreeView
        record_id = self.list_tab.car_table.focus()
        # The data values are retrieved from TreeView by its record_id.
        record_values = self.list_tab.car_table.item(record_id, 'values')
        print(record_values)
        attributes = self.get_car_attributes()
        # Make a dictionary with the attribute and StringVar
        for attr, value in zip(attributes, record_values):
            self.__current_car_data[attr].set(value)

    def clear_car_data(self, car_data):
        for strvar in car_data.values():
            strvar.set('')

    def field_data_to_dict(self, field_data):
        # Convert a pair of attribute and StringVar to
        # a tuple of attribute and the string in the StringVar
        return dict(map(
                        lambda pair: (pair[0], pair[1].get()),
                        field_data.items()
                        )
                    )

    # Dictionary of data which is filled in the common data field in the panel
    @property
    def current_car_data(self):
        return self.field_data_to_dict(self.__current_car_data)

    # Accessor to __current_car_data which is the common data field
    # in the panel
    @property
    def current_field(self):
        return self.__current_car_data

    def submit_request(self, car_data, db_function):
        for attr, value in car_data.items():
            print(attr + ': ' + value)

        try:
            car = Car(car_data)

        except ValidationError:
            print('Invalid value')

        else:
            if db_function(car.__dict__):
                self.notebook.select(self.list_tab.tab)
                self.list_tab.list_cars()
            else:
                print('submit request failed.')


def main():
    try:
        cars_db = CarsDB()
    except ServerNotReadyError:
        print('Server is not ready')
        exit(1)

    CarsPanel(cars_db)


if __name__ == '__main__':
    main()