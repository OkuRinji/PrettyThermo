import struct
import json
from pathlib import Path


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

    # Оставшиеся 88 байт (смещение 280) уже заполнены нулями

    return bytes(data)


def write_to_comp_ps(json_file: str, output_file: str, append: bool = True) -> int:
    """
    Записывает записи из JSON файла в бинарный файл COMP.PS.

    Args:
        json_file: Путь к JSON файлу с записями
        output_file: Путь к выходному бинарному файлу
        append: Если True, добавлять к существующему файлу, иначе создать новый

    Returns:
        Количество записанных записей
    """
    # Читаем JSON
    with open(json_file, "r", encoding="utf-8") as f:
        records = json.load(f)

    # Если append=True и файл существует, читаем существующие данные
    existing_data = b""
    if append and Path(output_file).exists():
        with open(output_file, "rb") as f:
            existing_data = f.read()

    # Сортируем записи по ID (по возрастанию)
    records = sorted(records, key=lambda r: r.get("id", 0))

    # Перезаписываем ID по порядку (1, 2, 3, ...)
    for i, record in enumerate(records, start=1):
        record["id"] = i

    # Записываем все записи
    with open(output_file, "wb") as f:
        # Сначала существующие данные
        if existing_data:
            f.write(existing_data)

        # Затем новые записи
        for record in records:
            record_bytes = write_record(record)
            f.write(record_bytes)

    return len(records)


def main():
    base_dir = Path(__file__).parent if "__file__" in globals() else Path.cwd()

    # Используем копии файлов
    json_file = base_dir / "components_copy.json"
    output_file = base_dir / "COMP.PS"

    if not json_file.exists():
        print(f"Ошибка: файл {json_file} не найден")
        return

    count = write_to_comp_ps(str(json_file), str(output_file), append=False)

    print(f"Записано {count} записей в {output_file}")
    print(f"Размер файла: {output_file.stat().st_size} байт")


if __name__ == "__main__":
    main()
