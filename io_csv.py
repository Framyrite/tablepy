# io_csv.py
import csv
from table import Table
from typing import Optional


def _is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def load_table(path: str, delimiter: str = ',', has_header: bool = True,
               encoding: str = 'utf-8', auto_detect_types: bool = True) -> Table:
    """
    Загружает CSV в Table.
    - пустые ячейки -> None
    - если has_header=True: первая строка — имена столбцов, иначе генерируются col0,col1,...
    - auto_detect_types: пытается автоматически определить типы числовых данных
    """
    try:
        with open(path, 'r', newline='', encoding=encoding) as f:
            reader = csv.reader(f, delimiter=delimiter)
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {path}")
    except Exception as e:
        raise IOError(f"Error reading CSV file {path}: {e}")

    if not rows:
        return Table(columns=[], rows=[])

    # Handle header
    if has_header:
        header = [col.strip() for col in rows[0]]
        data_rows = rows[1:]
    else:
        n_cols = len(rows[0])
        header = [f"col{i}" for i in range(n_cols)]
        data_rows = rows

    # Normalize rows
    normalized_rows = []
    for row_idx, row in enumerate(data_rows):
        normalized_row = []
        for i in range(len(header)):
            if i < len(row):
                value = row[i].strip()
                normalized_row.append(value if value != '' else None)
            else:
                normalized_row.append(None)
        normalized_rows.append(normalized_row)

    # Create table
    table = Table(columns=header, rows=normalized_rows)

    # Auto-detect types if requested
    if auto_detect_types and normalized_rows:
        type_suggestions = {}
        for col_idx, col_name in enumerate(header):
            # Get sample of non-None values
            sample_values = [row[col_idx] for row in normalized_rows if row[col_idx] is not None]
            if sample_values:
                first_val = sample_values[0]
                # Check if all values are integers
                if all(isinstance(v, str) and v.isdigit() for v in sample_values if v is not None):
                    type_suggestions[col_idx] = 'int'
                # Check if all values are floats
                elif all(isinstance(v, str) and _is_float(v) for v in sample_values if v is not None):
                    type_suggestions[col_idx] = 'float'

        if type_suggestions:
            table.set_column_types(type_suggestions)

    return table


def save_table(table: Table, path: str, delimiter: str = ',',
               has_header: bool = True, encoding: str = 'utf-8'):
    """
    Сохраняет Table в CSV файл.
    """
    try:
        with open(path, 'w', newline='', encoding=encoding) as f:
            writer = csv.writer(f, delimiter=delimiter)

            if has_header:
                writer.writerow(table.columns)

            for row in table.rows:
                # Convert None to empty string, other values to string
                csv_row = ['' if value is None else str(value) for value in row]
                writer.writerow(csv_row)

    except Exception as e:
        raise IOError(f"Error writing CSV file {path}: {e}")