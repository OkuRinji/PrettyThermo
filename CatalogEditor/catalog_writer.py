# core/catalog_writer.py
import struct
from pathlib import Path
from typing import List
from component import Component


def encode_string(value: str, length: int, encoding: str = "cp866") -> bytes:
    """Кодирует строку в байты заданной длины с паддингом нулями."""
    encoded = value.encode(encoding, errors="replace")
    if len(encoded) > length:
        encoded = encoded[:length]
    return encoded.ljust(length, b"\x00")


def write_record(record: dict) -> bytes:
    """
    Создаёт бинарную запись (372 байта) из словаря.

    Структура записи:
    - 4 байта: ID (int32, little-endian)
    - 124 байта: название вещества (cp866)
    - 128 байт: формула (cp866)
    - 16 байт: зарезервировано (нули)
    - 4 байта: enthalpy (float32, little-endian) по смещению 0x114 = 276
    - 88 байт: завершение (нули)
    """
    record_size = 372
    data = bytearray(record_size)

    # ID (4 байта, смещение 0)
    struct.pack_into("<i", data, 0, record.get("id", 0))

    # Название (124 байта, смещение 4)
    name = record.get("name", "")
    name_bytes = encode_string(name, 124)
    data[4:128] = name_bytes

    # Формула (128 байт, смещение 128)
    formula = record.get("formula", "")
    formula_bytes = encode_string(formula, 128)
    data[128:256] = formula_bytes

    # Зарезервировано (16 байт, смещение 256)
    # Уже заполнено нулями

    # Enthalpy (4 байта float32, смещение 0x114 = 276)
    enthalpy = float(record.get("enthalpy", 0.0))
    struct.pack_into("<f", data, 0x114, enthalpy)

    return bytes(data)


class CatalogWriter:
    """Класс для записи каталога компонентов в бинарный файл COMP.PS"""

    RECORD_SIZE = 372

    def write_components(
        self,
        components: List[Component],
        output_path: str,
        append: bool = False,
        reindex: bool = True,
    ) -> int:
        """
        Записывает компоненты в бинарный файл.

        Args:
            components: Список компонентов для записи
            output_path: Путь к выходному файлу COMP.PS
            append: Если True, добавить к существующему файлу
            reindex: Если True, пересчитать ID по порядку (1, 2, 3...)

        Returns:
            Количество записанных записей
        """
        # Читаем существующие данные если нужно
        existing_data = b""
        if append and Path(output_path).exists():
            with open(output_path, "rb") as f:
                existing_data = f.read()

        # Преобразуем компоненты в словари
        records = []
        for comp in components:
            records.append(
                {
                    "id": comp.id,
                    "name": comp.name,
                    "formula": comp.formula,
                    "enthalpy": comp.enthalpy if comp.enthalpy is not None else 0.0,
                }
            )

        # Сортируем по ID и пересчитываем если нужно
        records = sorted(records, key=lambda r: r.get("id", 0))
        if reindex:
            for i, record in enumerate(records, start=1):
                record["id"] = i

        # Записываем все записи
        with open(output_path, "wb") as f:
            # Сначала существующие данные
            if existing_data:
                f.write(existing_data)

            # Затем новые записи
            for record in records:
                record_bytes = write_record(record)
                f.write(record_bytes)

        return len(records)

    def read_components(self, input_path: str) -> List[Component]:
        """
        Читает компоненты из бинарного файла COMP.PS.

        Args:
            input_path: Путь к файлу COMP.PS

        Returns:
            Список компонентов
        """
        components = []
        record_size = self.RECORD_SIZE

        with open(input_path, "rb") as f:
            while True:
                data = f.read(record_size)
                if len(data) < record_size:
                    break

                # Читаем ID (4 байта)
                comp_id = struct.unpack_from("<i", data, 0)[0]

                # Читаем название (124 байта)
                name_bytes = data[4:128]
                name = (
                    name_bytes.rstrip(b"\x00").decode("cp866", errors="replace").strip()
                )

                # Читаем формулу (128 байт)
                formula_bytes = data[128:256]
                formula = (
                    formula_bytes.rstrip(b"\x00")
                    .decode("cp866", errors="replace")
                    .strip()
                )

                # Читаем энтальпию (4 байта float32, смещение 0x114 = 276)
                enthalpy = struct.unpack_from("<f", data, 0x114)[0]

                components.append(
                    Component(id=comp_id, name=name, formula=formula, enthalpy=enthalpy)
                )

        return components
