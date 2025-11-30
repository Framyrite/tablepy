# io_text.py
from table import Table


def save_table(table: Table, path: str, encoding: str = 'utf-8'):
    """
    Сохраняет текстовое представление таблицы (такое же, как print_table) в файл.
    """
    try:
        with open(path, 'w', encoding=encoding) as f:
            if not table.columns:
                f.write("Empty table\n")
                return

            # Calculate column widths
            widths = []
            for col_idx, col_name in enumerate(table.columns):
                max_width = len(str(col_name))
                for row in table.rows:
                    if col_idx < len(row):
                        value_str = "<None>" if row[col_idx] is None else str(row[col_idx])
                        max_width = max(max_width, len(value_str))
                widths.append(max_width)

            # Write header
            header = " | ".join(str(table.columns[i]).ljust(widths[i]) for i in range(len(table.columns)))
            separator = "-+-".join('-' * widths[i] for i in range(len(table.columns)))

            f.write(header + "\n")
            f.write(separator + "\n")

            # Write rows
            for row in table.rows:
                row_strs = []
                for i in range(len(table.columns)):
                    if i < len(row):
                        value = row[i]
                        value_str = "<None>" if value is None else str(value)
                    else:
                        value_str = "<None>"
                    row_strs.append(value_str.ljust(widths[i]))
                f.write(" | ".join(row_strs) + "\n")

    except Exception as e:
        raise IOError(f"Error writing text file {path}: {e}")