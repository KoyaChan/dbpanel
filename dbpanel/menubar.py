import tkinter as tk


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