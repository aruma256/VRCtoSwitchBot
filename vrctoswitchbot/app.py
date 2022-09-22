import json
import functools
from pathlib import Path
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
from typing import Any

from .action import Action
from .combobox_dialog import ComboboxDialog
from .switchbot.switchbot_device import SwitchBotDevice
from .switchbot.switchbot_controller import SwitchBotController
from .vrchat_osc.osc_listener import OSCListener
from .vrchat_osc.osc_sender import OSCSender
from . import lang
from . import version_checker

TITLE = 'VRC to SwitchBot'
VERSION = '0.3.0'
UPDATE_JSON_URL = 'https://github.com/aruma256/VRCtoSwitchBot/raw/main/version_info.json'  # noqa
CONFIG_PATH = Path('config.json')
N = 10


class App:

    def __init__(self):
        if not CONFIG_PATH.exists():
            self._generate_default_config()
        with open(CONFIG_PATH, encoding='utf-8') as f:
            self._config = config = json.load(f)
        self._actions: list[Action | None] = [None] * N
        self._switchbot_controller = SwitchBotController()
        self._osc_listener = OSCListener(app=self, **config['OSC']['listen'])
        self._osc_sender = OSCSender(**config['OSC']['send'])
        self._root = tk.Tk()
        self._create_menu()
        self._create_gui_elements()
        self._load_devices()
        threading.Thread(target=self._update_check, daemon=True).start()
        self._root.mainloop()

    def get_switchbot_controller(self) -> SwitchBotController:
        return self._switchbot_controller

    def get_osc_sender(self) -> OSCSender:
        return self._osc_sender

    def _load_devices(self):
        if 'actions' not in self._config:
            return
        for i, config_action in enumerate(self._config['actions']):
            if not config_action:
                continue
            device = SwitchBotDevice(config_action['device']['id'],
                                     config_action['device']['name'])
            action = Action(app=self,
                            exparam_name=config_action['expression_parameter'],
                            switchbot_device=device,
                            command=config_action['command'])
            self._register_action(i, action)

    def _generate_default_config(self):
        self._config = {
            'OSC': {
                'listen': {
                    'ip': '127.0.0.1',
                    'port': 9001,
                },
                'send': {
                    'ip': '127.0.0.1',
                    'port': 9000,
                },
            },
        }
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, ensure_ascii=False, indent=4)

    def _save(self):
        actions = []
        for action in self._actions:
            if action is None:
                actions.append(None)
                continue
            actions.append(
                {
                    'device': {
                        'id': action._switchbot_device.get_id(),
                        'name': action._switchbot_device.get_name(),
                    },
                    'expression_parameter': action._exparam_name,
                    'command': action._command,
                }
            )
        self._config['actions'] = actions
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
        if self._switchbot_controller.is_token_valid():
            status_message.set('済')
        else:
            status_message.set('トークン設定を行ってください')

        def button_callback():
            token = simpledialog.askstring('トークン設定', 'SwitchBotトークンを入力してください')
            if self._switchbot_controller.set_new_token(token):
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
        ttk.Label(frm, text='--対象ExParam--').grid(row=row, column=2)
        ttk.Label(frm, text='--対象デバイス名--').grid(row=row, column=3)
        ttk.Label(frm, text='--送信コマンド--').grid(row=row, column=4)
        #
        self._var_action_exparams = [tk.StringVar() for _ in range(N)]
        self._var_device_names = [tk.StringVar() for _ in range(N)]
        self._var_commands = [tk.StringVar() for _ in range(N)]

        def button_register_new_action_callback(i):
            d = ComboboxDialog(self._root,
                               self._switchbot_controller.get_device_name_list(),
                               title='操作対象のデバイスを選択してください')
            target_device_name = d.apply()
            target_device = None
            for device in self._switchbot_controller.get_device_list():
                if target_device_name == device.get_name():
                    target_device = device
            if target_device is None:
                messagebox.showerror('エラー', 'デバイスが見つかりません')
                return
            #
            d = ComboboxDialog(self._root, ['turnOff', 'turnOn'],
                               title='送信する操作コマンドを選んでください')
            command = d.apply().strip()
            if not command:
                messagebox.showerror('エラー', '操作が選択されていません')
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
            self._register_action(
                i,
                Action(self,
                       param_name,
                       target_device,
                       command)
            )
        #
        for action_i in range(N):
            row += 1

            def exec_action(i: int) -> None:
                if self._actions[i]:
                    self._actions[i].execute()

            elements = [
                ttk.Label(frm, text=f'アクション{action_i}'),
                ttk.Button(
                    frm,
                    command=functools.partial(button_register_new_action_callback, action_i),
                    text='設定する'),
                ttk.Label(
                    frm,
                    textvariable=self._var_action_exparams[action_i]),
                ttk.Label(
                    frm,
                    textvariable=self._var_device_names[action_i]),
                ttk.Label(
                    frm,
                    textvariable=self._var_commands[action_i]),
                ttk.Button(
                    frm,
                    text='手動実行',
                    command=functools.partial(exec_action, action_i),
                ),
                ttk.Button(
                    frm,
                    text='削除',
                    command=functools.partial(self._unregister_action, action_i),
                ),
            ]

            for elem_i, elem in enumerate(elements):
                elem.grid(row=row, column=elem_i)

    def _register_action(self, i: int, action: Action):
        self._actions[i] = action
        self._var_action_exparams[i].set(action._exparam_name)
        self._var_device_names[i].set(action._switchbot_device._name)
        self._var_commands[i].set(action._command)

    def _unregister_action(self, i: int):
        self._actions[i] = None
        self._var_action_exparams[i].set('')
        self._var_device_names[i].set('')
        self._var_commands[i].set('')

    def broadcast_osc(self, address: str, value: Any):
        for action in filter(None, self._actions):
            if action.is_acceptable(address):
                action.on_osc(address, value)

    def _update_check(self):
        if version_checker.is_newer_version_available(VERSION):
            messagebox.showinfo(message='新しいバージョンが公開されています')

    def kill(self):
        self._root.destroy()


def to_str(value):
    return f"{value:.2f}"
