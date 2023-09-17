import tkinter as tk


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
            self.panel.logger.error("Car to delete isn't found in db")
            self.panel.logger.error('car in db: %s', str(car_in_db))
            self.panel.logger.error('car to delete: %s', str(car_to_delete))
