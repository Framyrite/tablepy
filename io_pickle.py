# io_pickle.py
import pickle
from table import Table

def load_table(path: str) -> Table:
    """
    Загружает Table из pickle файла.
    """
    try:
        with open(path, 'rb') as f:
            data = pickle.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Pickle file not found: {path}")
    except Exception as e:
        raise IOError(f"Error reading pickle file {path}: {e}")

    # Handle different data formats
    if isinstance(data, Table):
        return data
    elif isinstance(data, dict):
        return Table.from_dict(data)
    else:
        raise TypeError(f"Unsupported data format in pickle file: {type(data)}")

def save_table(table: Table, path: str):
    """
    Сохраняет Table в pickle файл.
    """
    try:
        with open(path, 'wb') as f:
            # Save as dictionary representation for compatibility
            pickle.dump(table.as_dict(), f)
    except Exception as e:
        raise IOError(f"Error writing pickle file {path}: {e}")