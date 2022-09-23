import tkinter as tk
from tkinter import Widget, ttk
from tkinter import simpledialog


class ComboboxDialog(simpledialog.Dialog):
    def __init__(self, parent, choices: list[str], title: str | None = None) -> None:
        self.var_selected = tk.StringVar()
        self.choices = choices
        super().__init__(parent, title=title)

    def body(self, parent) -> Widget:
        combo = ttk.Combobox(parent, values=self.choices,
                             textvariable=self.var_selected)
        combo.grid(row=0, column=0)
        return combo

    def apply(self) -> str:
        return self.var_selected.get()
