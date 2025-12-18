# S03 – eda_cli: мини-EDA для CSV

Небольшое CLI-приложение для базового анализа CSV-файлов.
Используется в рамках Семинара 03 курса «Инженерия ИИ».

## Требования

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) установлен в систему

## Инициализация проекта

В корне проекта (S03):

```bash
uv sync
```

Эта команда:

- создаст виртуальное окружение `.venv`;
- установит зависимости из `pyproject.toml`;
- установит сам проект `eda-cli` в окружение.

## Запуск CLI

### Краткий обзор (`overview`)

```bash
uv run eda-cli overview data/example.csv
```

**Параметры:**

- `--sep` – разделитель (по умолчанию `,`);
- `--encoding` – кодировка (по умолчанию `utf-8`).

Выводит в консоль:
- размеры датасета (строки × столбцы)
- таблицу по колонкам: типы, пропуски, уникальные значения, статистики

## Полный EDA-отчёт (`report`)

```bash
uv run eda-cli report data/example.csv --out-dir reports
```

**Все параметры `report`:**

| Параметр | Описание | По умолчанию | Влияние на отчёт |
|----------|----------|--------------|------------------|
| `--out-dir` | Каталог для файлов отчёта | `reports` | Куда сохраняются все файлы |
| `--max-hist-columns` | Макс. числовых колонок для гистограмм | `6` | Сколько `hist_*.png` будет создано |
| `--top-k-categories` | Top-K значений для категориальных колонок | `5` | В `top_categories/*.csv` по K строк на колонку |
| `--title` | Заголовок отчёта | `EDA-отчёт` | H1 в начале `report.md` |
| `--min-missing-share` | Порог "проблемных" колонок по пропускам | `0.3` (30%) | Создаётся `problematic_missing_columns.csv` |

### Пример полного вызова:

uv run eda-cli report
data/titanic.csv
--out-dir reports_example
--max-hist-columns 4
--top-k-categories 8
--title "Titanic: EDA анализ"
--min-missing-share 0.2

В результате в каталоге `reports_example/` появятся:

- `report.md` – основной отчёт в Markdown;
- `summary.csv` – таблица по колонкам;
- `missing.csv` – пропуски по колонкам;
- `problematic_missing_columns.csv` – только "проблемные" (≥20% пропусков)
- `correlation.csv` – корреляционная матрица (если есть числовые признаки);
- `top_categories/*.csv` – top-k категорий по строковым признакам;
- `hist_*.png` – гистограммы числовых колонок;
- `missing_matrix.png` – визуализация пропусков;
- `correlation_heatmap.png` – тепловая карта корреляций.

### Эвристики качества данных (в `report.md`)

Отчёт включает автоматическую оценку качества:

- `quality_score` – Итоговый балл качества данных от 0 (плохо) до 1 (отлично).
- `max_missing_share` – Максимальная доля пропусков в самой "проблемной" колонке.
- `too_few_rows` – True, если строк меньше 100 — датасет слишком маленький для надёжного анализа.
- `too_many_columns` – True, если колонок больше 100 — датасет "широкий", много шума.
- `too_many_missing` – True, если max_missing_share > 50% — какая-то колонка почти полностью пустая.
- `has_constant_columns` – True, если есть колонка, где все ненулевые значения одинаковые (unique == 1, non_null > 0).
- `has_suspicious_id_duplicates` – True, если в колонках с "id" в названии (user_id, clientId и т.п.) есть дубликаты (unique != non_null).

## Тесты

```bash
uv run pytest -q
```

Что делает команда:

- `pytest` — запускает все unit-тесты проекта
- `-q (quiet)` — тихий режим, показывает только .... (4 точки = 4 теста пройдено)


## Быстрый старт

1. Установка

```uv sync```

2. Обзор датасета

```uv run eda-cli overview data/titanic.csv```

3. Полный отчёт

```uv run eda-cli report data/titanic.csv --out-dir reports```

4. Проверка

```cat reports/report.md```