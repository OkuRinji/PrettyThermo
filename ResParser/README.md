# ResParser - Парсер файлов .res

Парсер выходных файлов термохимической программы **TERMPS** (формат `.res`).

## Возможности

- Извлечение **всех расчётов** из файла (поддержка сетки расчётов)
- Характеристики продуктов сгорания:
  - Давление (P)
  - Температура (T)
  - Энтальпия (I)
  - Энтропия (S)
  - Теплоёмкость (C)
  - Плотность (R)
  - Молярная масса (M)
  - Показатель адиабаты (K)
- Равновесный состав газовой фазы (полный список компонентов)
- Конденсированные продукты реакции
- Процентный состав смеси для каждого расчёта
- Дата и время расчёта

## Установка

Требуется Python 3.10+

```bash
# Никаких дополнительных зависимостей не требуется
```

## Использование

### Базовое использование (CLI)

```bash
# Парсинг всех .res файлов в текущей директории
python res_parser.py

# Парсинг конкретного файла
python res_parser.py путь/к/файлу.res

# Парсинг всех файлов в директории
python res_parser.py путь/к/директории

# Экспорт в JSON
python res_parser.py файл.res json
```

### Использование как библиотеки

```python
from res_parser import parse_res_file, parse_directory, print_structured_data

# Парсинг одного файла
data = parse_res_file("1.RES")
print_structured_data(data)

# Доступ к расчётам
for calc in data.calculations:
    print(f"Расчёт #{calc.id}")
    print(f"  Температура: {calc.temperature} K")
    print(f"  Давление: {calc.pressure}")
    print(f"  Газовая фаза ({len(calc.equilibrium_gas)} компонентов): {calc.equilibrium_gas}")
    print(f"  Конденсированные продукты: {calc.equilibrium_condensed}")

# Парсинг всех файлов в директории
results = parse_directory("./res_files")
```

## Структура данных

### ResData

| Поле | Тип | Описание |
|------|-----|----------|
| `filename` | str | Имя файла |
| `mixture_name` | str | Название смеси |
| `mixture_density` | float | Плотность смеси |
| `components` | list[Component] | Компоненты смеси |
| `element_composition` | dict | Элементный состав |
| `calculations` | list[CalculationResult] | Список расчётов |

### CalculationResult

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | int | Номер расчёта |
| `composition_percent` | list[float] | Процентный состав смеси |
| `pressure` | float | Давление (P) |
| `temperature` | float | Температура (T), K |
| `enthalpy` | float | Энтальпия (I) |
| `entropy` | float | Энтропия (S) |
| `heat_capacity` | float | Теплоёмкость (C) |
| `density` | float | Плотность (R) |
| `molar_mass` | float | Молярная масса (M) |
| `adiabatic_index` | float | Показатель адиабаты (K) |
| `equilibrium_gas` | dict | Равновесный состав газовой фазы |
| `equilibrium_condensed` | dict | Конденсированные продукты |
| `calculation_date` | str | Дата расчёта |
| `calculation_time` | str | Время расчёта |

## Пример вывода

```
======================================================================
File: SNC.RES
======================================================================
Mixture: Горение без расширения

======================================================================
Number of calculations: 16
======================================================================

--- Calculation #1 ---
  Composition (%): [65.0001, 30.0, 5.0]
  Thermodynamic parameters:
    Pressure (P):        1.000000e-01
    Temperature (T):     1928.40 K
    Enthalpy (I):        -1067.90
    Entropy (S):         5.9237
  Equilibrium gas (6 components):
    HCl: 5.673800e-03
    MgH: 1.640400e-03
    ...
  Condensed products:
    MgO*: 8.160400e+00
  Date/Time: 18.09.08 10:20:41
```

## Пример JSON вывода

```bash
python res_parser.py SNC.RES json
```

```json
{
  "filename": "SNC.RES",
  "mixture_name": "Горение без расширения",
  "calculations": [
    {
      "id": 1,
      "composition_percent": [65.0001, 30.0, 5.0],
      "pressure": 0.1,
      "temperature": 1928.4,
      "enthalpy": -1067.9,
      "entropy": 5.9237,
      "equilibrium_gas": {
        "H2": 1.6292,
        "CO": 0.98451,
        ...
      },
      "equilibrium_condensed": {
        "MgO": 8.1604
      }
    }
  ]
}
```

## Формат файлов .res

Файлы `.res` - это выходные файлы программы TERMPS, содержащие результаты термохимических расчётов горения и взрыва. Файлы используют кодировку CP1251 (Windows-1251) и могут содержать несколько расчётов в одном файле (сетка по составу смеси и давлению).

## Лицензия

MIT
