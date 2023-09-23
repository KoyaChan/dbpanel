import os
from tkinter import messagebox
import configparser
import tkinter as tk


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
        self.logger = panel.logger

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
        self.logger.debug('dbchoice: %d', self.db_choice.get())
        # self.panel.log_debug('dbchoice: %d', self.db_choice.get())
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
