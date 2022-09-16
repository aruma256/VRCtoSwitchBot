import json
import functools
from pathlib import Path
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog

from .combobox_dialog import ComboboxDialog
from .target_device import TARGET_DEVICES, TargetDevice
from .osc_listener import OSCListener
from . import lang
from . import switchbot_controller
from . import version_checker

TITLE = 'VRC to SwitchBot'
VERSION = '0.2.4'
UPDATE_JSON_URL = 'https://github.com/aruma256/VRCtoSwitchBot/raw/main/version_info.json'  # noqa
CONFIG_PATH = Path('config.json')
N = 5


class GUI:

    def __init__(self):
        if not CONFIG_PATH.exists():
            self._generate_default_config()
        with open(CONFIG_PATH, encoding='utf-8') as f:
            self._config = config = json.load(f)
        self._root = tk.Tk()
        self._switchbot = switchbot_controller.SwitchBotController()
        self._osc_listener = OSCListener(**config['OSC'])
        self._create_menu()
        self._create_gui_elements()
        self._load_devices()
        threading.Thread(target=self._update_check, daemon=True).start()
        self._root.mainloop()

    def _load_devices(self):
        if 'device_config' not in self._config:
            return
        device_config = self._config['device_config']
        for i in range(N):
            if str(i) not in device_config:
                continue
            device = device_config[str(i)]
            print(device)
            TARGET_DEVICES[i] = TargetDevice(
                self._switchbot,
                device['device_id'],
                device['device_name'],
                device['expression_parameter'],
            )
            self._var_device_names[i].set(device['device_name'])
            self._var_device_exparams[i].set(device['expression_parameter'])

    def _generate_default_config(self):
        self._config = {
            "OSC": {
                "ip": "127.0.0.1",
                "port": 9001
            },
            "device_config": {},
        }
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, ensure_ascii=False, indent=4)

    def _save(self):
        device_config = {}
        for i, target_device in TARGET_DEVICES.items():
            device_config[str(i)] = {
                "device_name": target_device._name,
                "device_id": target_device.get_id(),
                "expression_parameter": target_device._param_name,
            }
        self._config['device_config'] = device_config
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, ensure_ascii=False, indent=4)
            messagebox.showinfo(message='保存しました')

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
        from tkinter import scrolledtext

        class AboutDialog(simpledialog.Dialog):
            def __init__(self, parent) -> None:
                super().__init__(parent, title=None)

            def body(self, parent):
                t = scrolledtext.ScrolledText(parent)
                t.insert(1.0, lang.ABOUT.format(VERSION=VERSION, LICENSE='dummy'))
                t.configure(state='disabled')
                t.grid(row=0, column=0)
                return t

        AboutDialog(self._root)

    def _show_lib_license(self) -> None:
        from tkinter import scrolledtext

        class LibLicenseDialog(simpledialog.Dialog):
            def __init__(self, parent) -> None:
                super().__init__(parent, title=None)

            def body(self, parent):
                t = scrolledtext.ScrolledText(parent)
                t.insert(1.0, lang.OSS_LICENSE.format(OSS_LICENSE='dummy'))
                t.configure(state='disabled')
                t.grid(row=0, column=0)
                return t

        LibLicenseDialog(self._root)

    def _create_gui_elements(self):
        self._root.geometry('600x400')
        self._root.protocol("WM_DELETE_WINDOW", self.kill)
        self._create_top_frame()
        self._create_settings_frame()

    def _create_top_frame(self):
        frm = ttk.Frame(self._root, padding=10)
        frm.grid()
        ttk.Label(frm, text=f"{TITLE} - v{VERSION}").grid(row=0, column=0)

    def _create_settings_frame(self):
        frm = ttk.Frame(self._root, padding=10)
        frm.grid()
        #
        row = 0
        status_message = tk.StringVar()
        if self._switchbot.is_token_valid():
            status_message.set('済')
        else:
            status_message.set('トークン設定を行ってください')

        def button_callback():
            token = simpledialog.askstring('トークン設定', 'SwitchBotトークンを入力してください')
            if self._switchbot.set_new_token(token):
                status_message.set('済')
            else:
                messagebox.showerror('エラー', '認証に失敗しました。')
        ttk.Button(
            frm,
            text='トークン設定',
            command=button_callback).grid(row=row, column=0)
        ttk.Label(
            frm,
            textvariable=status_message).grid(row=row, column=1)
        row += 1
        ttk.Button(
            frm,
            text='現在の設定を保存する',
            command=self._save,
        ).grid(row=row, column=0)
        #
        frm = ttk.Frame(self._root, padding=10)
        frm.grid()
        row = 0
        ttk.Label(frm, text='--ID--').grid(row=row, column=0)
        ttk.Label(frm, text='').grid(row=row, column=1)
        ttk.Label(frm, text='--対象デバイス名--').grid(row=row, column=2)
        ttk.Label(frm, text='--対象ExParam--').grid(row=row, column=3)
        #
        self._var_device_names = [tk.StringVar() for _ in range(N)]
        self._var_device_exparams = [tk.StringVar() for _ in range(N)]

        def button_config_callback(i):
            d = ComboboxDialog(self._root, device_names=self._switchbot.device_names)
            target_device_name = d.apply()
            target_device = None
            for device in self._switchbot.get_device_list():
                if target_device_name == device['deviceName']:
                    target_device = device
            if target_device is None:
                messagebox.showerror('エラー', 'デバイスが見つかりません')
                return
            #
            param_name = simpledialog.askstring(
                'ExpressionParameter設定',
                '紐づけるExpressionParameterの名前を入力してください',
                initialvalue='SwitchBot_Light')
            if param_name:
                param_name = param_name.strip()
            if not param_name:
                messagebox.showerror('エラー', 'ExpressionParameterの名前が不正です')
                return
            #
            target_device = TargetDevice(
                self._switchbot,
                target_device['deviceId'],
                target_device['deviceName'],
                param_name,
            )
            TARGET_DEVICES[i] = target_device
            self._var_device_names[i].set(target_device._name)
            self._var_device_exparams[i].set(target_device._param_name)
        #
        for device_i in range(N):
            row += 1

            def call_device_osc(i, value):
                if i in TARGET_DEVICES:
                    TARGET_DEVICES[i].on_osc(value)

            def clear_device(i):
                del TARGET_DEVICES[i]
                self._var_device_names[i].set('')
                self._var_device_exparams[i].set('')

            elements = [
                ttk.Label(frm, text=f'デバイス{device_i}'),
                ttk.Button(
                    frm,
                    command=functools.partial(button_config_callback, device_i),
                    text='設定する'),
                ttk.Label(
                    frm,
                    textvariable=self._var_device_names[device_i]),
                ttk.Label(
                    frm,
                    textvariable=self._var_device_exparams[device_i]),
                ttk.Button(
                    frm,
                    text='手動でON',
                    command=functools.partial(call_device_osc, device_i, True),
                ),
                ttk.Button(
                    frm,
                    text='手動でOFF',
                    command=functools.partial(call_device_osc, device_i, False),
                ),
                ttk.Button(
                    frm,
                    text='削除',
                    command=functools.partial(clear_device, device_i),
                ),
            ]

            for elem_i, elem in enumerate(elements):
                elem.grid(row=row, column=elem_i)

    def _update_check(self):
        if version_checker.is_newer_version_available(VERSION):
            messagebox.showinfo(message='新しいバージョンが公開されています')

    def kill(self):
        self._root.destroy()


def to_str(value):
    return f"{value:.2f}"
