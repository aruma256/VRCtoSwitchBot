import functools
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import simpledialog
from typing import TYPE_CHECKING

from .combobox_dialog import ComboboxDialog
from ..action import Action
from .. import const
from .. import lang

if TYPE_CHECKING:
    from ..app import App


class GUIWindow:

    def __init__(self, app: 'App') -> None:
        self._app = app
        self._root = tk.Tk()
        self._create_menu()
        self._create_gui_elements()

    def mainloop(self) -> None:
        self._root.mainloop()

    def _create_menu(self) -> None:
        menu_root = tk.Menu(self._root)
        self._root.config(menu=menu_root)
        #
        self._create_menu_info(menu_root)

    def _create_menu_info(self, menu_root: tk.Menu) -> None:
        menu_info = tk.Menu(self._root)
        menu_info.add_command(label='About', command=self._show_about)
        menu_info.add_command(label='OSS license', command=self._show_lib_license)
        menu_root.add_cascade(label='Info', menu=menu_info)

    def _show_about(self) -> None:

        class AboutDialog(simpledialog.Dialog):
            def __init__(self, parent) -> None:
                super().__init__(parent, title=None)

            def body(self, parent) -> scrolledtext.ScrolledText:
                t = scrolledtext.ScrolledText(parent)
                t.insert(1.0, lang.ABOUT.format(VERSION=const.VERSION, LICENSE='dummy'))
                t.configure(state='disabled')
                t.grid(row=0, column=0)
                return t

        AboutDialog(self._root)

    def _show_lib_license(self) -> None:

        class LibLicenseDialog(simpledialog.Dialog):
            def __init__(self, parent) -> None:
                super().__init__(parent, title=None)

            def body(self, parent) -> scrolledtext.ScrolledText:
                t = scrolledtext.ScrolledText(parent)
                t.insert(1.0, lang.OSS_LICENSE.format(OSS_LICENSE='dummy'))
                t.configure(state='disabled')
                t.grid(row=0, column=0)
                return t

        LibLicenseDialog(self._root)

    def _create_gui_elements(self) -> None:
        self._root.geometry('800x400')
        self._root.protocol("WM_DELETE_WINDOW", self.kill)
        self._create_top_frame()
        self._create_settings_frame()

    def _create_top_frame(self) -> None:
        frm = ttk.Frame(self._root, padding=10)
        frm.grid()
        ttk.Label(frm, text=f"{const.TITLE} - v{const.VERSION}").grid(row=0, column=0)

    def _create_settings_frame(self) -> None:
        frm = ttk.Frame(self._root, padding=10)
        frm.grid()
        #
        row = 0
        status_message = tk.StringVar()
        if self._app.get_switchbot_controller().is_token_valid():
            status_message.set('???')
        else:
            status_message.set('??????????????????????????????????????????')

        def button_callback() -> None:
            token = simpledialog.askstring('??????????????????', 'SwitchBot???????????????????????????????????????')
            if self._app.get_switchbot_controller().set_new_token(token):
                status_message.set('???')
            else:
                messagebox.showerror('?????????', '??????????????????????????????')

        ttk.Button(
            frm,
            text='??????????????????',
            command=button_callback).grid(row=row, column=0)
        ttk.Label(
            frm,
            textvariable=status_message).grid(row=row, column=1)
        row += 1
        ttk.Button(
            frm,
            text='??????????????????????????????',
            command=self._app.save,
        ).grid(row=row, column=0)
        #
        frm = ttk.Frame(self._root, padding=10)
        frm.grid()
        row = 0
        ttk.Label(frm, text='--ID--').grid(row=row, column=0)
        ttk.Label(frm, text='').grid(row=row, column=1)
        ttk.Label(frm, text='--??????ExParam--').grid(row=row, column=2)
        ttk.Label(frm, text='--?????????????????????--').grid(row=row, column=3)
        ttk.Label(frm, text='--??????????????????--').grid(row=row, column=4)
        #
        self._var_action_osc_addresses = [tk.StringVar() for _ in range(const.N)]
        self._var_device_names = [tk.StringVar() for _ in range(const.N)]
        self._var_commands = [tk.StringVar() for _ in range(const.N)]

        def button_register_new_action_callback(i) -> None:
            d = ComboboxDialog(self._root,
                               self._app.get_switchbot_controller().get_device_name_list(),
                               title='??????????????????????????????????????????????????????')
            target_device_name = d.apply()
            target_device = None
            for device in self._app.get_switchbot_controller().get_device_list():
                if target_device_name == device.get_name():
                    target_device = device
            if target_device is None:
                messagebox.showerror('?????????', '????????????????????????????????????')
                return
            #
            d = ComboboxDialog(self._root, ['turnOff', 'turnOn'],
                               title='??????????????????????????????????????????????????????')
            command = d.apply().strip()
            if not command:
                messagebox.showerror('?????????', '????????????????????????????????????')
                return
            #
            osc_address = simpledialog.askstring(
                'ExpressionParameter??????',
                '????????????OSC??????????????????????????????????????????\n'
                '?????????/avatar/parameters/(ExpressionParameter?????????) ?????????????????????????????????\n'
                '??? : /avatar/parameters/SwitchBot_Light_On',
                initialvalue='/avatar/parameters/XXXXXXXXXX')
            if osc_address:
                osc_address = osc_address.strip()
            if not osc_address:
                messagebox.showerror('?????????', 'ExpressionParameter????????????????????????')
                return
            #
            self._app.register_action(
                i,
                Action(self._app,
                       osc_address,
                       target_device,
                       command)
            )
        #
        for action_i in range(const.N):
            row += 1

            def exec_action(i: int) -> None:
                action = self._app.get_action(i)
                if action:
                    action.execute()

            elements = [
                ttk.Label(frm, text=f'???????????????{action_i}'),
                ttk.Button(
                    frm,
                    command=functools.partial(button_register_new_action_callback, action_i),
                    text='????????????'),
                ttk.Label(
                    frm,
                    textvariable=self._var_action_osc_addresses[action_i]),
                ttk.Label(
                    frm,
                    textvariable=self._var_device_names[action_i]),
                ttk.Label(
                    frm,
                    textvariable=self._var_commands[action_i]),
                ttk.Button(
                    frm,
                    text='????????????',
                    command=functools.partial(exec_action, action_i),
                ),
                ttk.Button(
                    frm,
                    text='??????',
                    command=functools.partial(self._app.unregister_action, action_i),
                ),
            ]

            for elem_i, elem in enumerate(elements):
                elem.grid(row=row, column=elem_i)

    def set_action(self, i: int, action: Action) -> None:
        self._var_action_osc_addresses[i].set(action._osc_address)
        self._var_device_names[i].set(action._switchbot_device._name)
        self._var_commands[i].set(action._command)

    def clear_action(self, i: int) -> None:
        self._var_action_osc_addresses[i].set('')
        self._var_device_names[i].set('')
        self._var_commands[i].set('')

    def show_info(self, message: str) -> None:
        messagebox.showinfo(message=message)

    def kill(self) -> None:
        self._root.destroy()
