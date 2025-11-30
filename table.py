# table.py
from copy import deepcopy
from typing import List, Any, Dict, Optional, Iterable, Union


class TableError(Exception):
    pass


class ColumnTypeError(TableError):
    pass


class Table:
    TYPE_STRS = {'int': int, 'float': float, 'bool': bool, 'str': str}

    def __init__(self,
                 columns: Optional[List[str]] = None,
                 rows: Optional[List[List[Any]]] = None,
                 types: Optional[Dict[Union[int, str], Union[type, str]]] = None):

        self.columns = list(columns) if columns else []
        self.rows = [list(r) for r in rows] if rows else []

        # Validate row lengths match columns
        if self.columns and self.rows:
            for i, r in enumerate(self.rows):
                if len(r) != len(self.columns):
                    raise TableError(f"Row {i} length {len(r)} doesn't match columns {len(self.columns)}")

        # Initialize types
        self.types: Dict[Union[int, str], type] = {}

        # Set default types first
        for idx in range(len(self.columns)):
            self.types[idx] = str

        # Apply provided types - ИСПРАВЛЕНИЕ: не пытаемся автоматически определить by_number
        if types:
            # Просто сохраняем переданные типы без автоматического применения
            # Они будут применены только когда явно вызван set_column_types
            for key, type_spec in types.items():
                self.types[key] = self._normalize_type(type_spec)

    def _col_index(self, column: Union[int, str]) -> int:
        if isinstance(column, int):
            if not (0 <= column < len(self.columns)):
                raise IndexError(f"Column index {column} out of range [0, {len(self.columns) - 1}]")
            return column
        if isinstance(column, str):
            if column not in self.columns:
                raise KeyError(f"Column name '{column}' not found. Available: {self.columns}")
            return self.columns.index(column)
        raise TypeError(f"Column must be int or str, got {type(column)}")

    def _type_for(self, column: Union[int, str]) -> type:
        # Try by exact key first
        if column in self.types:
            return self._normalize_type(self.types[column])

        # Try by index
        idx = self._col_index(column)
        if idx in self.types:
            return self._normalize_type(self.types[idx])

        # Fallback to string
        return str

    def _normalize_type(self, t: Union[str, type]) -> type:
        if isinstance(t, str):
            if t not in self.TYPE_STRS:
                raise ColumnTypeError(f"Unknown type string '{t}'. Available: {list(self.TYPE_STRS.keys())}")
            return self.TYPE_STRS[t]
        if t in (int, float, bool, str):
            return t
        raise ColumnTypeError(f"Unsupported type {t}")

    def _convert_value(self, value: Any, to_type: type) -> Any:
        if value is None:
            return None

        if isinstance(value, to_type):
            return value

        try:
            if to_type is bool:
                if isinstance(value, str):
                    v = value.strip().lower()
                    if v in ('true', '1', 'yes', 'y', 't'):
                        return True
                    if v in ('false', '0', 'no', 'n', 'f'):
                        return False
                    raise ValueError(f"Cannot convert '{value}' to bool")
                return bool(value)
            return to_type(value)
        except Exception as e:
            raise ColumnTypeError(f"Cannot convert value {value!r} to {to_type.__name__}: {e}")

    def as_dict(self) -> Dict[str, Any]:
        return {
            'columns': deepcopy(self.columns),
            'rows': deepcopy(self.rows),
            'types': deepcopy(self.types)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Table':
        return cls(
            columns=data.get('columns'),
            rows=data.get('rows'),
            types=data.get('types')
        )

    def get_rows_by_number(self, start: int, stop: Optional[int] = None, copy_table: bool = False) -> 'Table':
        if not self.rows:
            return Table(columns=self.columns, rows=[], types=self.types.copy())

        if not isinstance(start, int) or start < 0:
            raise TypeError("start must be non-negative integer")

        n = len(self.rows)
        if start >= n:
            raise IndexError(f"start row {start} out of range [0, {n - 1}]")

        if stop is None:
            row_slice = [start]
        else:
            if not isinstance(stop, int):
                raise TypeError("stop must be integer")
            if stop < start:
                raise ValueError(f"stop ({stop}) must be >= start ({start})")
            if stop >= n:
                raise IndexError(f"stop row {stop} out of range [0, {n - 1}]")
            row_slice = list(range(start, stop + 1))

        selected_rows = []
        for idx in row_slice:
            if copy_table:
                selected_rows.append(deepcopy(self.rows[idx]))
            else:
                selected_rows.append(self.rows[idx])

        return Table(columns=self.columns, rows=selected_rows, types=self.types.copy())

    def get_rows_by_index(self, *vals: Any, copy_table: bool = False) -> 'Table':
        if not self.columns:
            raise TableError("No columns in table")
        if not vals:
            return Table(columns=self.columns, rows=[], types=self.types.copy())

        matches = []
        for r in self.rows:
            if r and r[0] in vals:
                if copy_table:
                    matches.append(deepcopy(r))
                else:
                    matches.append(r)

        return Table(columns=self.columns, rows=matches, types=self.types.copy())

    def get_column_types(self, by_number: bool = True) -> Dict[Union[int, str], type]:
        result = {}
        for idx, name in enumerate(self.columns):
            t = self._type_for(idx)
            key = idx if by_number else name
            result[key] = t
        return result

    def set_column_types(self, types_dict: Dict[Union[int, str], Union[type, str]], by_number: bool = True):
        if not isinstance(types_dict, dict):
            raise TypeError("types_dict must be a dictionary")

        # First validate all types and keys
        normalized_types = {}
        for key, type_spec in types_dict.items():
            if by_number:
                if not isinstance(key, int):
                    raise TypeError("When by_number=True, keys must be integers")
                if key < 0 or key >= len(self.columns):
                    raise IndexError(f"Column index {key} out of range [0, {len(self.columns) - 1}]")
                col_key = key
            else:
                if not isinstance(key, str):
                    raise TypeError("When by_number=False, keys must be strings")
                if key not in self.columns:
                    raise KeyError(f"Column name '{key}' not found")
                col_key = key

            normalized_types[col_key] = self._normalize_type(type_spec)

        # Then apply conversions
        for col_key, new_type in normalized_types.items():
            idx = self._col_index(col_key)

            # Convert existing values
            for i, row in enumerate(self.rows):
                try:
                    row[idx] = self._convert_value(row[idx], new_type)
                except ColumnTypeError as e:
                    raise ColumnTypeError(f"Row {i}, column {col_key}: {e}") from e

            # Update type mapping
            self.types[col_key] = new_type

    def get_values(self, column: Union[int, str] = 0) -> List[Any]:
        idx = self._col_index(column)
        col_type = self._type_for(column)

        result = []
        for i, row in enumerate(self.rows):
            try:
                result.append(self._convert_value(row[idx], col_type))
            except ColumnTypeError as e:
                raise ColumnTypeError(f"Row {i}: {e}") from e

        return result

    def get_value(self, column: Union[int, str] = 0) -> Any:
        if len(self.rows) != 1:
            raise TableError(f"get_value requires exactly one row, got {len(self.rows)}")
        return self.get_values(column)[0]

    def set_values(self, values: Iterable[Any], column: Union[int, str] = 0):
        idx = self._col_index(column)
        col_type = self._type_for(column)
        values_list = list(values)

        if len(values_list) != len(self.rows):
            raise TableError(f"Values length {len(values_list)} doesn't match rows count {len(self.rows)}")

        for i, value in enumerate(values_list):
            try:
                self.rows[i][idx] = self._convert_value(value, col_type)
            except ColumnTypeError as e:
                raise ColumnTypeError(f"Row {i}: {e}") from e

    def set_value(self, value: Any, column: Union[int, str] = 0):
        if len(self.rows) != 1:
            raise TableError(f"set_value requires exactly one row, got {len(self.rows)}")
        self.set_values([value], column)

    def print_table(self):
        if not self.columns:
            print("Empty table")
            return

        widths = []
        for c in range(len(self.columns)):
            max_width = len(str(self.columns[c]))
            for row in self.rows:
                if c < len(row):
                    value_str = "<None>" if row[c] is None else str(row[c])
                    max_width = max(max_width, len(value_str))
            widths.append(max_width)

        # Header
        header = " | ".join(str(self.columns[i]).ljust(widths[i]) for i in range(len(self.columns)))
        separator = "-+-".join('-' * widths[i] for i in range(len(self.columns)))

        print(header)
        print(separator)

        # Rows
        for row in self.rows:
            row_strs = []
            for i in range(len(self.columns)):
                if i < len(row):
                    value = row[i]
                    value_str = "<None>" if value is None else str(value)
                else:
                    value_str = "<None>"
                row_strs.append(value_str.ljust(widths[i]))
            print(" | ".join(row_strs))

    def _binary_column_op(self, col_a: Union[int, str], col_b_or_scalar: Union[int, str, Any],
                          operation, operation_name: str, result_column: Optional[Union[int, str]] = None):
        idx_a = self._col_index(col_a)
        type_a = self._type_for(col_a)

        # Determine if second operand is column or scalar
        is_column = False
        if isinstance(col_b_or_scalar, (int, str)):
            try:
                self._col_index(col_b_or_scalar)
                is_column = True
            except (IndexError, KeyError):
                is_column = False

        results = []
        if is_column:
            idx_b = self._col_index(col_b_or_scalar)
            type_b = self._type_for(col_b_or_scalar)

            for i, row in enumerate(self.rows):
                val_a = row[idx_a]
                val_b = row[idx_b]

                if val_a is None or val_b is None:
                    results.append(None)
                    continue

                try:
                    # Convert both to float for arithmetic operations to ensure compatibility
                    converted_a = float(self._convert_value(val_a, type_a))
                    converted_b = float(self._convert_value(val_b, type_b))
                    results.append(operation(converted_a, converted_b))
                except Exception as e:
                    raise TableError(f"{operation_name} failed at row {i}: {e}") from e
        else:
            scalar = col_b_or_scalar
            for i, row in enumerate(self.rows):
                val_a = row[idx_a]

                if val_a is None:
                    results.append(None)
                    continue

                try:
                    # Convert to float and ensure scalar is also numeric
                    converted_a = float(self._convert_value(val_a, type_a))
                    converted_scalar = float(scalar)  # Convert scalar to float
                    results.append(operation(converted_a, converted_scalar))
                except Exception as e:
                    raise TableError(f"{operation_name} failed at row {i}: {e}") from e

        # Handle result column
        if result_column is not None:
            # Create new column if needed
            if isinstance(result_column, int):
                if result_column < 0 or result_column > len(self.columns):
                    raise IndexError(f"Result column index {result_column} out of range")

                if result_column == len(self.columns):
                    # Add new column
                    new_name = f"col{result_column}"
                    self.columns.append(new_name)
                    for row in self.rows:
                        row.append(None)
            else:
                if result_column not in self.columns:
                    # Add new named column
                    self.columns.append(result_column)
                    for row in self.rows:
                        row.append(None)

            # Set the values
            result_idx = self._col_index(result_column)
            for i, value in enumerate(results):
                self.rows[i][result_idx] = value

            # Set type for new column (infer from first non-None result)
            if result_column not in self.types:
                for result_val in results:
                    if result_val is not None:
                        self.types[result_column] = type(result_val)
                        break
                else:
                    self.types[result_column] = str

            return None
        else:
            return results

    def add(self, col_a, col_b_or_scalar, result_column: Optional[Union[int, str]] = None):
        return self._binary_column_op(col_a, col_b_or_scalar, lambda x, y: x + y, 'add', result_column)

    def sub(self, col_a, col_b_or_scalar, result_column: Optional[Union[int, str]] = None):
        return self._binary_column_op(col_a, col_b_or_scalar, lambda x, y: x - y, 'sub', result_column)

    def mul(self, col_a, col_b_or_scalar, result_column: Optional[Union[int, str]] = None):
        return self._binary_column_op(col_a, col_b_or_scalar, lambda x, y: x * y, 'mul', result_column)

    def div(self, col_a, col_b_or_scalar, result_column: Optional[Union[int, str]] = None):
        def safe_divide(x, y):
            if y == 0:
                raise ZeroDivisionError("Division by zero")
            return x / y

        return self._binary_column_op(col_a, col_b_or_scalar, safe_divide, 'div', result_column)

    def _comparison_op(self, col_a, col_b_or_scalar, comparator, op_name: str):
        idx_a = self._col_index(col_a)
        type_a = self._type_for(col_a)

        is_column = False
        if isinstance(col_b_or_scalar, (int, str)):
            try:
                self._col_index(col_b_or_scalar)
                is_column = True
            except (IndexError, KeyError):
                is_column = False

        results = []
        if is_column:
            idx_b = self._col_index(col_b_or_scalar)
            type_b = self._type_for(col_b_or_scalar)

            for i, row in enumerate(self.rows):
                val_a = row[idx_a]
                val_b = row[idx_b]

                if val_a is None or val_b is None:
                    results.append(False)
                else:
                    try:
                        converted_a = self._convert_value(val_a, type_a)
                        converted_b = self._convert_value(val_b, type_b)
                        results.append(bool(comparator(converted_a, converted_b)))
                    except Exception as e:
                        raise TableError(f"{op_name} failed at row {i}: {e}") from e
        else:
            scalar = col_b_or_scalar
            for i, row in enumerate(self.rows):
                val_a = row[idx_a]

                if val_a is None:
                    results.append(False)
                else:
                    try:
                        converted_a = self._convert_value(val_a, type_a)
                        results.append(bool(comparator(converted_a, scalar)))
                    except Exception as e:
                        raise TableError(f"{op_name} failed at row {i}: {e}") from e

        return results

    def eq(self, col_a, col_b_or_scalar):
        return self._comparison_op(col_a, col_b_or_scalar, lambda x, y: x == y, 'eq')

    def gr(self, col_a, col_b_or_scalar):
        return self._comparison_op(col_a, col_b_or_scalar, lambda x, y: x > y, 'gr')

    def ls(self, col_a, col_b_or_scalar):
        return self._comparison_op(col_a, col_b_or_scalar, lambda x, y: x < y, 'ls')

    def ge(self, col_a, col_b_or_scalar):
        return self._comparison_op(col_a, col_b_or_scalar, lambda x, y: x >= y, 'ge')

    def le(self, col_a, col_b_or_scalar):
        return self._comparison_op(col_a, col_b_or_scalar, lambda x, y: x <= y, 'le')

    def ne(self, col_a, col_b_or_scalar):
        return self._comparison_op(col_a, col_b_or_scalar, lambda x, y: x != y, 'ne')

    def filter_rows(self, bool_list: Iterable[bool], copy_table: bool = False) -> 'Table':
        bools = list(bool_list)
        if len(bools) != len(self.rows):
            raise TableError(f"Boolean list length {len(bools)} doesn't match rows count {len(self.rows)}")

        filtered_rows = []
        for i, keep in enumerate(bools):
            if keep:
                if copy_table:
                    filtered_rows.append(deepcopy(self.rows[i]))
                else:
                    filtered_rows.append(self.rows[i])

        return Table(columns=self.columns, rows=filtered_rows, types=self.types.copy())