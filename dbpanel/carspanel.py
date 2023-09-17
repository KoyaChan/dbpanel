import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import configparser
import logging
if __name__ == '__main__':
    from listtab import ListTab
    from addtab import AddTab
    from updatetab import UpdateTab
    from deletetab import DeleteTab
    from carsdb import Car
    from carsdb import CarsDB
    from carsdb import ValidationError
    from carsdb import ServerNotReadyError
    from carscsv import CarsCSV
else:
    from .listtab import ListTab
    from .addtab import AddTab
    from .updatetab import UpdateTab
    from .deletetab import DeleteTab
    from .carsdb import Car
    from .carsdb import CarsDB
    from .carsdb import ValidationError
    from .carsdb import ServerNotReadyError
    from .carscsv import CarsCSV


# To do :
# - Clear panel.__current_car_data after delete_car succeeds
# - When user enters an id in DeleteTab or UpdateTab page then its data is set to panel.__current_car_data
# - Show new id value to be assigned in AddTab automatically


# Config window to configure some settings
class ConfigWindow():
    CONFIG_FILE = './dbpanel.ini'
    DEFAULT = {
        'default': {
            # comment
            '# DB Choice': None,
            '#  1: json': None,
            '#  2: csv': None,
            'db': '1',
        }
    }
    DB_CHOICE = {
        'json': 1,
        'csv': 2,
    }

    def __init__(self, panel):
        self.panel = panel
        self.parent = panel.root
        self.db_choice = tk.IntVar(self.panel.root)
        self.config = configparser.ConfigParser(
            delimiters='=',
            allow_no_value=True     # to write comments
        )
        self.read_config()

    def create_modal_dialog(self):
        modal_dlg = tk.Toplevel(self.parent)
        modal_dlg.grab_set()
        modal_dlg.focus_set()
        modal_dlg.geometry('200x200')
        # Don't show in the task bar
        modal_dlg.transient(self.parent)
        self.modal_dlg = modal_dlg

        config_frame = tk.Frame(modal_dlg)

        choices = self.DB_CHOICE

        num = 1
        for choice, value in choices.items():
            button = tk.Radiobutton(config_frame,
                                    text=choice,
                                    value=value,
                                    variable=self.db_choice,
                                    command=self.switch_db,
                                    )
            button.grid(row=1, column=num)
            num += 1

        db_choice_label = tk.Label(config_frame,
                                   text='DB Choice')
        db_choice_label.grid(row=0,
                             column=0,
                             columnspan=num,
                             )

        save_button = tk.Button(config_frame,
                                text='Save',
                                command=self.save_config)
        save_button.grid(row=3,
                         column=0,
                         columnspan=num,
                         )

        self.save_button = save_button

        config_frame.pack()

    def switch_db(self):
        self.panel.log_debug('dbchoice: %d', self.db_choice.get())
        want_restart = messagebox.askyesno('Need restart panel',
                                           'Need to restart to switch db.\n'
                                           'Stop now ?',
                                           # show message over the dialog
                                           parent=self.modal_dlg,
                                           )
        self.parent.lower()

        if want_restart:
            self.save_config()
            self.parent.destroy()
        else:
            return

    def save_config(self):
        self.config.read_dict(self.DEFAULT)

        if not self.config.has_section('DB Choice'):
            self.config.add_section('DB Choice')

        self.config['DB Choice']['db'] = str(self.db_choice.get())
        with open(self.CONFIG_FILE, 'w') as configfile:
            self.config.write(configfile)

        self.modal_dlg.destroy()

    def read_config(self):
        if os.path.exists(self.CONFIG_FILE):
            self.config.read(self.CONFIG_FILE)
            self.db_choice.set(int(self.config['DB Choice']['db']))
        else:
            self.db_choice.set(self.DB_CHOICE['json'])      # default is json

    # Convert the digit value in self.db_choice to the db name in DB_CHOICE.
    def chosen_db_name(self):
        return next(name for name, choice in self.DB_CHOICE.items()
                    if choice == self.db_choice.get())


class MenuBar():
    def __init__(self, panel):
        self.panel = panel
        self.parent = panel.root
        self.menu_bar = tk.Menu(self.parent)
        self.parent.config(menu=self.menu_bar)
        self.add_sub_menus()

    def add_sub_menus(self):
        self.add_file_menu()
        self.add_option_menu()

    def make_submenu(self, label, parent=None, underline=None):
        if parent is None:
            parent = self.menu_bar

        sub_menu = tk.Menu(parent, tearoff=0)

        if underline is None:
            parent.add_cascade(label=label,
                               menu=sub_menu)
        else:
            parent.add_cascade(label=label,
                               menu=sub_menu,
                               underline=underline)

        return sub_menu

    def add_file_menu(self):
        self.sub_menu_file = self.make_submenu('File', underline=0)
        self.sub_menu_file.add_command(label='Quit',
                                       underline=0,
                                       command=lambda: self.parent.destroy())

    def add_option_menu(self):
        self.sub_menu_config = self.make_submenu('Option',
                                                 underline=0)
        self.sub_menu_config.add_command(label='Config',
                                         command=self.panel.config_window.create_modal_dialog,
                                         underline=0)


class CarsPanel:
    LOG_FORMAT = '%(asctime)s:%(name)s:%(levelname)s:%(message)s'
    DB_CLASSES = {
        'json': CarsDB,
        'csv': CarsCSV,
    }

    def __init__(self):
        self.root = tk.Tk()
        self.logger = self.logging_setup()
        self.config_window = ConfigWindow(self)
        self.choose_db()
        self.root.title('Cars DB : ' + self.db_name)
        self.menu_bar = MenuBar(self)
        self.car_attributes = None

        self.notebook = ttk.Notebook(self.root)
        self.__current_car_data = self.make_car_data_fields()
        self.make_tabs()
        self.notebook.pack()

        self.root.mainloop()

    # Return db object based on the choice in the config window
    # Default is json db
    def choose_db(self):
        self.db_name = self.config_window.chosen_db_name()
        try:
            self.db = self.DB_CLASSES[self.db_name]()
        except ServerNotReadyError:
            self.log_error('Server not ready.')
            exit(1)

    def logging_setup(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        log_handler = logging.StreamHandler()
        # log_handler = logging.FileHandler('dbpanel.log', 'a')
        log_formatter = logging.Formatter(self.LOG_FORMAT)
        log_handler.setFormatter(log_formatter)
        log_handler.setLevel(logging.DEBUG)
        logger.addHandler(log_handler)
        return logger

    def log_info(self, message, *args):
        if len(args):
            self.logger.info(message, *args)
        else:
            self.logger.info(message)

    def log_debug(self, message, *args):
        if len(args):
            self.logger.debug(message, *args)
        else:
            self.logger.debug(message)

    def log_error(self, message, *args):
        if len(args):
            self.logger.error(message, *args)
        else:
            self.logger.error(message)

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
            # Prevent id field from being edited
            entry = tk.Entry(input_frame,
                             textvariable=car_data_fields[attr],
                             state='disabled' if attr == 'id' else 'normal'
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
        self.logger.debug('current car data: %s', str(record_values))
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
            self.logger.debug('%s : %s', attr, value)

        try:
            car = Car(car_data)

        except ValidationError:
            self.logger.error('Invalid value')

        else:
            if db_function(car.__dict__):
                self.notebook.select(self.list_tab.tab)
                self.list_tab.list_cars()
            else:
                self.logger.error('submit request failed.')


def main():
    CarsPanel()


if __name__ == '__main__':
    main()
