import json
import functools
from pathlib import Path
import requests
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog

from .target_device import TARGET_DEVICES, TargetDevice
from .osc_listener import OSCListener
from . import switchbot_controller

TITLE = 'VRC to SwitchBot'
VERSION = '0.1.0'
UPDATE_JSON_URL = 'https://github.com/aruma256/VRCtoSwitchBot/raw/main/version_info.json' # noqa
CONFIG_PATH = Path('config.json')
N = 5


def _is_local_version_outdated(remote_version, local_version):
    remote = tuple(map(int, remote_version.split('.')))
    local = tuple(map(int, local_version.split('.')))
    return remote > local

class ComboboxDialog(simpledialog.Dialog):
    def __init__(self, parent, device_list, title=None):
        self.device_list = device_list
        super().__init__(parent, title=title)
    def body(self, parent):
        self.var_selected = tk.StringVar()
        ttk.Combobox(parent, values=self.device_list, textvariable=self.var_selected).grid(row=0, column=0)
    def apply(self):
        return self.var_selected.get()

class GUI:

    def __init__(self):
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        self._root = tk.Tk()
        self._switchbot = switchbot_controller.SwitchBotController()
        self._osc_listener = OSCListener(**config['OSC'])
        self._create_gui_elements()
        threading.Thread(target=self._update_check, daemon=True).start()
        self._root.mainloop()

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
        #
        frm = ttk.Frame(self._root, padding=10)
        frm.grid()
        row = 0
        ttk.Label(frm, text='--ID--').grid(row=row, column=0)
        ttk.Label(frm, text='').grid(row=row, column=1)
        ttk.Label(frm, text='--対象デバイス名--').grid(row=row, column=2)
        ttk.Label(frm, text='--対象ExParam--').grid(row=row, column=3)
        #
        var_device_names = [tk.StringVar() for _ in range(N)]
        var_device_exparams = [tk.StringVar() for _ in range(N)]
        def button_config_callback(i):
            d = ComboboxDialog(self._root, device_list=self._switchbot.device_names)
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
            var_device_names[i].set(target_device._name)
            var_device_exparams[i].set(target_device._param_name)
        #
        for i in range(N):
            row += 1
            ttk.Label(
                frm,
                text=f'デバイス{i}'
            ).grid(row=row, column=0)
            ttk.Button(
                frm,
                command=functools.partial(button_config_callback, i),
                text='設定する').grid(row=row, column=1)
            ttk.Label(frm, textvariable=var_device_names[i]).grid(row=row, column=2)
            ttk.Label(frm, textvariable=var_device_exparams[i]).grid(row=row, column=3)
            def call_device_osc(i, value):
                if i in TARGET_DEVICES:
                    TARGET_DEVICES[i].on_osc(value)
            ttk.Button(
                frm, text='手動でON',
                command=functools.partial(call_device_osc, i, True),
                ).grid(row=row, column=4)
            ttk.Button(
                frm, text='手動でOFF',
                command=functools.partial(call_device_osc, i, False),
                ).grid(row=row, column=5)

    def _update_check(self):
        try:
            res = requests.get(UPDATE_JSON_URL, timeout=5)
            if res.status_code == 200:
                data = res.json()
                if _is_local_version_outdated(data['recommended'], VERSION):
                    messagebox.showinfo(message='新しいバージョンが公開されています')
        except Exception:
            pass

    def kill(self):
        self._root.destroy()

def to_str(value):
    return f"{value:.2f}"
