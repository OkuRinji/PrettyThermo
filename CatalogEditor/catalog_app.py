#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отдельное приложение: Редактор каталога компонентов
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List
import json
from pathlib import Path
import sys

from catalog import Catalog
from catalog_writer import CatalogWriter
from component import Component


def get_base_path():
    """Получить базовый путь: для exe - папка с exe, для .py - папка проекта"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent.parent


class CatalogEditorApp:
    """Редактор каталога компонентов для работы с бинарной базой COMP.PS"""

    def __init__(self, root):
        self.root = root
        self.root.title("Редактор каталога компонентов")
        self.root.geometry("1000x700")

        self.catalog = Catalog()
        self.writer = CatalogWriter()

        # Список компонентов для редактирования
        self.edit_components: List[Component] = []

        # Пути к файлам - TERMO в проекте
        self.base_dir = get_base_path() / "TERMO"
        self.comp_ps_path = tk.StringVar(value=str(self.base_dir / "COMP.PS"))
        self.json_path = tk.StringVar(value=str(self.base_dir / "components.json"))

        self._create_widgets()
        self._load_catalog()

    def _create_widgets(self):
        """Создает все виджеты окна"""

        # Панель инструментов
        toolbar = ttk.Frame(self.root, padding=10)
        toolbar.pack(fill="x")

        ttk.Button(
            toolbar, text="📂 Загрузить JSON", command=self._load_json, width=15
        ).pack(side="left", padx=5)
        ttk.Button(
            toolbar,
            text="📂 Загрузить из COMP.PS",
            command=self._load_from_comp_ps,
            width=20,
        ).pack(side="left", padx=5)
        ttk.Button(
            toolbar, text="💾 Сохранить в JSON", command=self._save_json, width=18
        ).pack(side="left", padx=5)
        ttk.Button(
            toolbar,
            text="💾 Записать в COMP.PS",
            command=self._write_to_comp_ps,
            width=20,
        ).pack(side="left", padx=5)

        ttk.Label(toolbar, text="|").pack(side="left", padx=10)
        ttk.Button(
            toolbar, text="➕ Добавить", command=self._add_component, width=12
        ).pack(side="left", padx=5)
        ttk.Button(
            toolbar, text="✏️ Редактировать", command=self._edit_component, width=16
        ).pack(side="left", padx=5)
        ttk.Button(
            toolbar, text="🗑️ Удалить", command=self._delete_component, width=12
        ).pack(side="left", padx=5)

        # Статус
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(
            self.root, textvariable=self.status_var, relief="sunken", padding=5
        )
        status_bar.pack(fill="x", padx=5, pady=2)

        # Таблица компонентов
        tree_frame = ttk.Frame(self.root, padding=10)
        tree_frame.pack(fill="both", expand=True)

        columns = ("id", "name", "formula", "enthalpy")
        self.tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings", height=12
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Название")
        self.tree.heading("formula", text="Формула")
        self.tree.heading("enthalpy", text="Энтальпия (кДж/кг)")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("name", width=300)
        self.tree.column("formula", width=250)
        self.tree.column("enthalpy", width=90, anchor="e")

        # Скроллбары
        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scroll = ttk.Scrollbar(
            tree_frame, orient="horizontal", command=self.tree.xview
        )
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")

        # Двойной клик для редактирования
        self.tree.bind("<Double-1>", lambda e: self._edit_component())

        # Панель путей
        paths_frame = ttk.LabelFrame(self.root, text="Пути к файлам", padding=10)
        paths_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(paths_frame, text="COMP.PS:").grid(
            row=0, column=0, sticky="w", pady=2
        )
        ttk.Entry(paths_frame, textvariable=self.comp_ps_path, width=60).grid(
            row=0, column=1, padx=5, pady=2, sticky="ew"
        )
        ttk.Button(paths_frame, text="Обзор...", command=self._browse_comp_ps).grid(
            row=0, column=2, pady=2
        )

        ttk.Label(paths_frame, text="JSON:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(paths_frame, textvariable=self.json_path, width=60).grid(
            row=1, column=1, padx=5, pady=2, sticky="ew"
        )
        ttk.Button(paths_frame, text="Обзор...", command=self._browse_json).grid(
            row=1, column=2, pady=2
        )

        paths_frame.columnconfigure(1, weight=1)

        # Инфо
        info_frame = ttk.LabelFrame(self.root, text="Информация", padding=10)
        info_frame.pack(fill="x", padx=10, pady=5)

        self.info_var = tk.StringVar(
            value="Выберите компонент для просмотра информации"
        )
        ttk.Label(info_frame, textvariable=self.info_var, wraplength=900).pack(
            anchor="w"
        )

        self.tree.bind("<<TreeviewSelect>>", lambda e: self._update_info())

        # Меню
        self._create_menu()

    def _create_menu(self):
        """Создает главное меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(
            label="Загрузить JSON...", command=self._load_json, accelerator="Ctrl+O"
        )
        file_menu.add_command(
            label="Загрузить из COMP.PS...", command=self._load_from_comp_ps
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Сохранить в JSON...", command=self._save_json, accelerator="Ctrl+S"
        )
        file_menu.add_command(
            label="Записать в COMP.PS...", command=self._write_to_comp_ps
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Выход", command=self.root.quit, accelerator="Alt+F4"
        )

        # Правка
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        edit_menu.add_command(
            label="Добавить", command=self._add_component, accelerator="Ctrl+N"
        )
        edit_menu.add_command(
            label="Редактировать", command=self._edit_component, accelerator="Ctrl+E"
        )
        edit_menu.add_command(
            label="Удалить", command=self._delete_component, accelerator="Delete"
        )

        # Привязки клавиш
        self.root.bind("<Control-o>", lambda e: self._load_json())
        self.root.bind("<Control-s>", lambda e: self._save_json())
        self.root.bind("<Control-n>", lambda e: self._add_component())
        self.root.bind("<Control-e>", lambda e: self._edit_component())
        self.root.bind("<Delete>", lambda e: self._delete_component())

    def _load_catalog(self):
        """Загружает каталог из JSON по умолчанию"""
        if self.catalog.get_count() == 0:
            json_path = Path(self.json_path.get())
            if json_path.exists():
                self.catalog.load_from_json(str(json_path))
        self._refresh_tree()

    def _refresh_tree(self):
        """Обновляет таблицу компонентов"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.edit_components = self.catalog.get_all()

        for comp in self.edit_components:
            self.tree.insert(
                "",
                "end",
                values=(
                    comp.id,
                    comp.name,
                    comp.formula,
                    f"{comp.enthalpy:.2f}" if comp.enthalpy is not None else "N/A",
                ),
            )

        self.status_var.set(f"Загружено компонентов: {len(self.edit_components)}")

    def _load_json(self):
        """Загружает компоненты из JSON файла"""
        filepath = filedialog.askopenfilename(
            title="Загрузить JSON",
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")],
        )
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Очищаем текущий каталог и загружаем новый
                self.catalog = Catalog()
                for item in data:
                    comp = Component(
                        id=item.get("id", 0),
                        name=item.get("name", ""),
                        formula=item.get("formula", ""),
                        enthalpy=item.get("enthalpy", 0.0),
                    )
                    self.catalog.add_component(comp)

                self.json_path.set(filepath)
                self._refresh_tree()
                messagebox.showinfo(
                    "Успех", f"Загружено {self.catalog.get_count()} компонентов"
                )
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить JSON:\n{e}")

    def _save_json(self):
        """Сохраняет компоненты в JSON файл"""
        filepath = filedialog.asksaveasfilename(
            title="Сохранить JSON",
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")],
        )
        if filepath:
            try:
                data = []
                for comp in self.edit_components:
                    data.append(
                        {
                            "id": comp.id,
                            "name": comp.name,
                            "formula": comp.formula,
                            "enthalpy": comp.enthalpy
                            if comp.enthalpy is not None
                            else 0.0,
                        }
                    )

                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                self.json_path.set(filepath)
                messagebox.showinfo("Успех", f"Сохранено {len(data)} компонентов")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить JSON:\n{e}")

    def _load_from_comp_ps(self):
        """Загружает компоненты из бинарного файла COMP.PS"""
        filepath = filedialog.askopenfilename(
            title="Загрузить из COMP.PS",
            defaultextension=".ps",
            filetypes=[("COMP.PS файлы", "*.ps"), ("Все файлы", "*.*")],
        )
        if filepath:
            try:
                components = self.writer.read_components(filepath)

                # Очищаем текущий каталог и загружаем новый
                self.catalog = Catalog()
                for comp in components:
                    self.catalog.add_component(comp)

                self.comp_ps_path.set(filepath)
                self._refresh_tree()
                messagebox.showinfo(
                    "Успех",
                    f"Загружено {self.catalog.get_count()} компонентов из COMP.PS",
                )
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить из COMP.PS:\n{e}")

    def _write_to_comp_ps(self):
        """Записывает компоненты в бинарный файл COMP.PS"""
        if not self.edit_components:
            messagebox.showwarning(
                "Внимание", "Сначала загрузите или добавьте компоненты"
            )
            return

        filepath = filedialog.asksaveasfilename(
            title="Записать в COMP.PS",
            defaultextension=".ps",
            initialfile="COMP.PS",
            filetypes=[("COMP.PS файлы", "*.ps"), ("Все файлы", "*.*")],
        )
        if filepath:
            try:
                count = self.writer.write_components(
                    self.edit_components, filepath, append=False, reindex=True
                )
                self.comp_ps_path.set(filepath)
                messagebox.showinfo(
                    "Успех",
                    f"Записано {count} компонентов в COMP.PS\nID пересчитаны по порядку (1, 2, 3...)",
                )
                self._refresh_tree()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось записать в COMP.PS:\n{e}")

    def _add_component(self):
        """Добавляет новый компонент"""
        dialog = ComponentDialog(self.root, title="Добавить компонент")
        component = dialog.get_component()

        if component:
            # Добавляем в каталог
            self.catalog.add_component(component)
            self.edit_components.append(component)
            self._refresh_tree()

    def _edit_component(self):
        """Редактирует выбранный компонент"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите компонент для редактирования")
            return

        item = self.tree.item(selection[0])
        comp_id = int(item["values"][0])
        comp = self.catalog.get_by_id(comp_id)

        if not comp:
            return

        dialog = ComponentDialog(
            self.root, component=comp, title="Редактировать компонент"
        )
        updated = dialog.get_component()

        if updated:
            # Обновляем в каталоге
            self.catalog.update_component(updated)
            self._refresh_tree()

    def _delete_component(self):
        """Удаляет выбранный компонент"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите компонент для удаления")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранный компонент?"):
            item = self.tree.item(selection[0])
            comp_id = int(item["values"][0])
            comp = self.catalog.get_by_id(comp_id)

            if comp:
                # Удаляем из каталога
                self.catalog.delete_component(comp_id)

                # Удаляем из списка редактирования
                self.edit_components = [
                    c for c in self.edit_components if c.id != comp_id
                ]
                self._refresh_tree()

    def _update_info(self):
        """Обновляет информацию о выбранном компоненте"""
        selection = self.tree.selection()
        if not selection:
            self.info_var.set("Выберите компонент для просмотра информации")
            return

        item = self.tree.item(selection[0])
        comp_id = int(item["values"][0])
        comp = self.catalog.get_by_id(comp_id)

        if comp:
            info = f"ID: {comp.id}\n"
            info += f"Название: {comp.name}\n"
            info += f"Формула: {comp.formula}\n"
            info += (
                f"Энтальпия: {comp.enthalpy:.2f} кДж/кг"
                if comp.enthalpy
                else "Энтальпия: N/A"
            )
            self.info_var.set(info)

    def _browse_comp_ps(self):
        """Выбор файла COMP.PS"""
        filepath = filedialog.askopenfilename(
            title="Выбрать COMP.PS",
            defaultextension=".ps",
            filetypes=[("COMP.PS файлы", "*.ps"), ("Все файлы", "*.*")],
        )
        if filepath:
            self.comp_ps_path.set(filepath)

    def _browse_json(self):
        """Выбор JSON файла"""
        filepath = filedialog.askopenfilename(
            title="Выбрать JSON",
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")],
        )
        if filepath:
            self.json_path.set(filepath)


class ComponentDialog:
    """Диалог для добавления/редактирования компонента"""

    def __init__(self, parent, component: Component = None, title: str = "Компонент"):
        self.parent = parent
        self.component = component
        self.result: Component = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Центрирование
        self.dialog.update_idletasks()
        x = (parent.winfo_width() // 2) - (500 // 2)
        y = (parent.winfo_height() // 2) - (300 // 2)
        self.dialog.geometry(f"+{x}+{y}")

        self._create_widgets()
        if component:
            self._load_component(component)

    def _create_widgets(self):
        """Создает виджеты диалога"""

        # ID
        id_frame = ttk.Frame(self.dialog, padding=10)
        id_frame.pack(fill="x")
        ttk.Label(id_frame, text="ID:").pack(side="left")
        self.id_entry = ttk.Entry(id_frame, width=20)
        self.id_entry.pack(side="left", padx=5)
        ttk.Label(id_frame, text="(пересчитывается автоматически)").pack(side="left")

        # Название
        name_frame = ttk.Frame(self.dialog, padding=10)
        name_frame.pack(fill="x")
        ttk.Label(name_frame, text="Название:").pack(side="left")
        self.name_entry = ttk.Entry(name_frame, width=50)
        self.name_entry.pack(side="left", padx=5)

        # Формула
        formula_frame = ttk.Frame(self.dialog, padding=10)
        formula_frame.pack(fill="x")
        ttk.Label(formula_frame, text="Формула:").pack(side="left")
        self.formula_entry = ttk.Entry(formula_frame, width=50)
        self.formula_entry.pack(side="left", padx=5)

        # Энтальпия
        enthalpy_frame = ttk.Frame(self.dialog, padding=10)
        enthalpy_frame.pack(fill="x")
        ttk.Label(enthalpy_frame, text="Энтальпия (кДж/кг):").pack(side="left")
        self.enthalpy_entry = ttk.Entry(enthalpy_frame, width=20)
        self.enthalpy_entry.pack(side="left", padx=5)

        # Кнопки
        btn_frame = ttk.Frame(self.dialog, padding=10)
        btn_frame.pack(fill="x")

        ttk.Button(btn_frame, text="OK", command=self._on_ok, width=15).pack(
            side="left", padx=5
        )
        ttk.Button(
            btn_frame, text="Отмена", command=self.dialog.destroy, width=15
        ).pack(side="left", padx=5)

    def _load_component(self, comp: Component):
        """Загружает данные компонента в поля"""
        self.id_entry.insert(0, str(comp.id))
        self.name_entry.insert(0, comp.name)
        self.formula_entry.insert(0, comp.formula)
        if comp.enthalpy is not None:
            self.enthalpy_entry.insert(0, f"{comp.enthalpy:.2f}")

    def _on_ok(self):
        """Сохраняет данные и закрывает диалог"""
        try:
            comp_id = int(self.id_entry.get().strip() or 0)
            name = self.name_entry.get().strip()
            formula = self.formula_entry.get().strip()
            enthalpy_str = self.enthalpy_entry.get().strip()
            enthalpy = float(enthalpy_str) if enthalpy_str else None

            if not name:
                messagebox.showwarning("Внимание", "Введите название компонента")
                return

            self.result = Component(
                id=comp_id, name=name, formula=formula, enthalpy=enthalpy
            )
            self.dialog.destroy()

        except ValueError as e:
            messagebox.showerror("Ошибка", f"Проверьте числовые значения:\n{e}")

    def get_component(self) -> Component:
        """Возвращает результат после закрытия диалога"""
        self.parent.wait_window(self.dialog)
        return self.result


if __name__ == "__main__":
    root = tk.Tk()
    app = CatalogEditorApp(root)
    root.mainloop()
