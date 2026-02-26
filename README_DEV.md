# PrettyThermo — Руководство разработчика

## Структура проекта

```
PrettyThermo/
├── App/                    # Основное приложение ThermoApp
│   ├── main.py            # Точка входа GUI
│   ├── config.py          # Конфигурация
│   ├── core/              # Бизнес-логика
│   │   ├── catalog_manager.py
│   │   ├── ps_generator.py
│   │   ├── res_parser.py
│   │   └── runner.py
│   └── gui/               # GUI компоненты
│       └── params_dialog.py
├── CatalogEditor/         # Редактор каталога компонентов
│   ├── catalog_app.py     # Точка входа
│   ├── catalog.py         # Модель каталога
│   ├── catalog_writer.py  # Чтение/запись бинарных файлов
│   └── component.py       # Модель компонента
├── TERMO/                 # Рабочая директория TERMO94
│   ├── COMP.PS            # Бинарная база компонентов
│   └── components.json    # JSON каталог компонентов
├── Release/               # Скомпилированные .exe файлы
├── requirements.txt       # Зависимости Python
└── build.bat              # Скрипт сборки (требует доработки)
```

## Требования

- Python 3.10+
- PyInstaller 6.0+ (для сборки .exe)

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Запуск в режиме разработки

### Основное приложение
```bash
cd App
python main.py
```

### Редактор каталога
```bash
cd CatalogEditor
python catalog_app.py
```

## Сборка исполняемых файлов

### Автоматическая сборка
```bash
build.bat
```

### Ручная сборка

**ThermoApp:**
```bash
python -m PyInstaller --onefile --name "ThermoApp" ^
    --add-data "App\core;core" ^
    --add-data "App\gui;gui" ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.ttk ^
    --hidden-import=tkinter.messagebox ^
    --hidden-import=tkinter.filedialog ^
    --console ^
    App\main.py
```

**CatalogEditor:**
```bash
python -m PyInstaller --onefile --name "CatalogEditor" ^
    --add-data "CatalogEditor\catalog.py;." ^
    --add-data "CatalogEditor\catalog_writer.py;." ^
    --add-data "CatalogEditor\component.py;." ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.ttk ^
    --hidden-import=tkinter.messagebox ^
    --hidden-import=tkinter.filedialog ^
    --console ^
    CatalogEditor\catalog_app.py
```

## Важные замечания по сборке

### Проблема с путями
При сборке в один файл (`--onefile`) PyInstaller распаковывает всё во временную папку. Для корректной работы используйте функцию:

```python
import sys
from pathlib import Path

def get_base_path():
    """Получить базовый путь"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent.parent
```

### Структура путей в приложениях
Оба приложения ищут папку `TERMO/` относительно своего расположения:
- При запуске из `.exe` — папка рядом с exe-файлом
- При запуске из `.py` — `../TERMO/` от скрипта

## Архитектура

### ThermoApp
1. **CatalogManager** — загрузка/сохранение каталога компонентов
2. **PSGenerator** — генерация входных файлов `.PS` для TERMO94
3. **ResParser** — парсинг результатов расчёта из `.RES` файлов
4. **DOSBoxRunner** — запуск TERMO94 через DOSBox
5. **ParamsDialog** — диалог ввода параметров расчёта

### CatalogEditor
1. **Catalog** — управление коллекцией компонентов
2. **Component** — модель компонента (ID, название, формула, энтальпия)
3. **CatalogWriter** — чтение/запись бинарного формата COMP.PS

## Формат COMP.PS

Бинарный файл базы компонентов:
- Заголовок: 4 байта (количество компонентов, little-endian uint32)
- Записи компонентов (по 128 байт каждая):
  - ID: 4 байта (int32)
  - Название: 60 байт (ASCII, null-terminated)
  - Формула: 56 байт (ASCII, null-terminated)
  - Энтальпия: 8 байт (float64, little-endian)

## Расширение функциональности

### Добавление нового модуля
1. Создайте модуль в `App/core/` или `CatalogEditor/`
2. Добавьте импорт в основной файл
3. При сборке укажите `--add-data` для новых файлов

### Добавление GUI элементов
Все GUI элементы используют `tkinter` и `ttk`. Стили:
- Кнопки: `ttk.Button(..., width=15)`
- Поля ввода: `tk.Entry(..., width=20)`
- Таблицы: `ttk.Treeview(..., columns=(...), show='headings')`

## Отладка

### Логирование
Добавьте вывод в консоль (при сборке с `--console`):
```python
print(f"[DEBUG] Path: {some_path}")
```

### Проверка путей
```python
import sys
print(f"sys.executable: {sys.executable}")
print(f"sys.frozen: {getattr(sys, 'frozen', False)}")
print(f"__file__: {__file__}")
```

## Тестирование

1. Проверьте работу из исходников
2. Проверьте работу из `.exe`
3. Проверьте пути к файлам `TERMO/`
4. Проверьте запуск TERMO94 через DOSBox

## Контакты

Вопросы и предложения: [указать контакты]
