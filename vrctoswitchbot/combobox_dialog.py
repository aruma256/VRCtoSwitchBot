import tkinter as tk
from tkinter import Widget, ttk
from tkinter import simpledialog
from typing import List


class ComboboxDialog(simpledialog.Dialog):
    def __init__(self, parent, device_names: List[str], title: str | None = None) -> None:
        self.var_selected = tk.StringVar()
        self.device_names = device_names
        super().__init__(parent, title=title)

    def body(self, parent) -> Widget:
        combo = ttk.Combobox(parent, values=self.device_names,
                             textvariable=self.var_selected)
        combo.grid(row=0, column=0)
        return combo

    def apply(self) -> str:
        return self.var_selected.get()
