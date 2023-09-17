import tkinter as tk


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
