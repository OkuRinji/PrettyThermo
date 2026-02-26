# CatalogEditor/catalog.py
"""
Локальный класс Catalog для управления компонентами
Не зависит от core.catalog_manager
"""

from typing import Dict, List, Optional
from component import Component


class Catalog:
    """Менеджер каталога компонентов (локальная версия для CatalogEditor)"""

    def __init__(self):
        self.components: Dict[int, Component] = {}
        self.name_index: Dict[str, int] = {}

    def load_from_json(self, filepath: str) -> bool:
        """Загрузка каталога из JSON файла"""
        import json
        from pathlib import Path

        path = Path(filepath)
        if not path.exists():
            return False

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            for item in data:
                comp = Component(
                    id=item.get("id", 0),
                    name=item.get("name", ""),
                    formula=item.get("formula", ""),
                    enthalpy=item.get("enthalpy", 0.0),
                )
                self.components[comp.id] = comp
                self.name_index[comp.name.lower()] = comp.id

            return True
        except Exception as e:
            print(f"Ошибка загрузки каталога: {e}")
            return False

    def save_to_json(self, filepath: str, components: List[Component]) -> bool:
        """Сохранение каталога в JSON файл"""
        import json

        try:
            data = []
            for comp in components:
                data.append(
                    {
                        "id": comp.id,
                        "name": comp.name,
                        "formula": comp.formula,
                        "enthalpy": comp.enthalpy if comp.enthalpy is not None else 0.0,
                    }
                )

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"Ошибка сохранения каталога: {e}")
            return False

    def search(self, query: str) -> List[Component]:
        """Поиск компонентов по названию или формуле"""
        query_lower = query.lower()
        results = []

        for comp in self.components.values():
            if (
                query_lower in comp.name.lower()
                or query_lower in comp.formula.lower()
                or str(comp.id) == query
            ):
                results.append(comp)

        return sorted(results, key=lambda x: x.id)

    def get_by_id(self, comp_id: int) -> Optional[Component]:
        """Получение компонента по ID"""
        return self.components.get(comp_id)

    def get_by_ids(self, ids: List[int]) -> List[Component]:
        """Получение нескольких компонентов по ID"""
        return [self.components[i] for i in ids if i in self.components]

    def get_all(self) -> List[Component]:
        """Получение всех компонентов (отсортировано по ID)"""
        return sorted(self.components.values(), key=lambda x: x.id)

    def get_count(self) -> int:
        """Получение количества компонентов"""
        return len(self.components)

    def add_component(self, comp: Component) -> None:
        """Добавление компонента"""
        self.components[comp.id] = comp
        self.name_index[comp.name.lower()] = comp.id

    def update_component(self, comp: Component) -> None:
        """Обновление компонента"""
        # Находим старое имя и удаляем из индекса
        for name, cid in list(self.name_index.items()):
            if cid == comp.id:
                del self.name_index[name]
                break

        self.components[comp.id] = comp
        self.name_index[comp.name.lower()] = comp.id

    def delete_component(self, comp_id: int) -> bool:
        """Удаление компонента по ID"""
        comp = self.get_by_id(comp_id)
        if comp:
            if comp.name.lower() in self.name_index:
                del self.name_index[comp.name.lower()]
            del self.components[comp_id]
            return True
        return False

    def clear(self) -> None:
        """Очистка каталога"""
        self.components.clear()
        self.name_index.clear()
