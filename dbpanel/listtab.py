import tkinter as tk
from tkinter import ttk


# Tab page in the panel where all data fields are listed.
# When a row is clicked in the list, its data is read into
# CarsPanel.__current_car_data.
class ListTab():
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

        # Adjust the height of the Treeview with the number of rows
        self.car_table.config(height=len(cars))

        for car in cars:
            # insert the data of a row into the bottm of the table
            self.car_table.insert(parent='',
                                  index='end',
                                  values=tuple(car.values())
                                  )
