import json
from pathlib import Path
import requests
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog

from .osc_listener import OSCListener
from . import switchbot_controller

TITLE = 'VRC to SwitchBot'
VERSION = '0.1.0'
UPDATE_JSON_URL = 'https://github.com/aruma256/VRCtoSwitchBot/raw/main/version_info.json' # noqa
CONFIG_PATH = Path('config.json')


def _is_local_version_outdated(remote_version, local_version):
    remote = tuple(map(int, remote_version.split('.')))
    local = tuple(map(int, local_version.split('.')))
    return remote > local

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
        self._root.geometry('400x400')
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
        token_status_message = tk.StringVar()
        if self._switchbot.is_token_valid():
            token_status_message.set('ロード済み')
        else:
            token_status_message.set('トークンを入力してください')
        def token_button_callback():
            pass
            token = simpledialog.askstring('セットアップ', 'SwitchBotのトークンを入力してください')
            if token:
                token = token.strip()
            if self._switchbot.set_new_token(token):
                token_status_message.set('保存済み')
                devicelist_button_callback()
            else:
                messagebox.showerror('エラー', '認証に失敗しました')
                token_status_message.set('再設定してください')
        ttk.Label(frm, text='step1 トークン設定').grid(row=row, column=0)
        ttk.Button(
            frm,
            text='初期設定',
            command=token_button_callback).grid(row=row, column=1)
        ttk.Label(
            frm, textvariable=token_status_message).grid(row=row, column=2)
        #
        row += 1
        devicelist_status_message = tk.StringVar()
        if self._switchbot.get_device_list():
            devicelist_status_message.set('自動取得済み')
        else:
            devicelist_status_message.set('')
        def devicelist_button_callback():
            if self._switchbot.fetch_device_list():
                devicelist_status_message.set('取得済み')
        ttk.Label(frm, text='step2 デバイスリスト取得').grid(row=row, column=0)
        ttk.Button(
            frm,
            text='取得する',
            command=devicelist_button_callback).grid(row=row, column=1)
        ttk.Label(
            frm, textvariable=devicelist_status_message).grid(row=row, column=2)
        #
        row += 1
        ttk.Combobox(frm, )

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
