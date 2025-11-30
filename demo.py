# demo_extended_fixed.py
from table import Table, TableError
from io_csv import load_table as load_csv, save_table as save_csv
from io_pickle import load_table as load_pickle, save_table as save_pickle
from io_text import save_table as save_text


def demo_basic_operations():
    print("=== 1. БАЗОВЫЕ ОПЕРАЦИИ С ТАБЛИЦАМИ ===\n")

    # Создание таблицы
    columns = ['id', 'name', 'age', 'salary', 'is_active']
    rows = [
        [1, 'Андрей', '25', '50000', 'True'],
        [2, 'Иван', '30', '75000', 'True'],
        [3, 'Роман', '22', '45000', 'False'],
        [4, 'Давид', '35', '90000', 'True'],
        [5, 'Анна', '28', '60000', 'True']
    ]

    t = Table(columns=columns, rows=rows)
    print("Исходная таблица:")
    t.print_table()

    # Установка типов данных - ИСПРАВЛЕНИЕ: явно указываем by_number=False
    print("\n1.1 Установка типов столбцов:")
    t.set_column_types({'id': 'int', 'age': 'int', 'salary': 'float', 'is_active': 'bool'}, by_number=False)
    print("Типы столбцов:", t.get_column_types(by_number=False))

    # Получение значений
    print("\n1.2 Получение значений:")
    print("Зарплаты:", t.get_values('salary'))
    print("Возраста:", t.get_values('age'))
    print("Активность:", t.get_values('is_active'))

    return t


def demo_row_operations(table):
    print("\n=== 2. ОПЕРАЦИИ СО СТРОКАМИ ===\n")

    # Получение строк по номерам
    print("2.1 Строки 0-2:")
    t1 = table.get_rows_by_number(0, 2, copy_table=True)
    t1.print_table()

    # Получение строк по индексу (первый столбец)
    print("\n2.2 Строки с id=1 и id=4:")
    t2 = table.get_rows_by_index(1, 4, copy_table=True)
    t2.print_table()

    # Получение одной строки
    print("\n2.3 Одна строка (индекс 1):")
    t3 = table.get_rows_by_number(1, copy_table=True)
    t3.print_table()
    print("Значение зарплаты в этой строке:", t3.get_value('salary'))


def demo_arithmetic_operations(table):
    print("\n=== 3. АРИФМЕТИЧЕСКИЕ ОПЕРАЦИИ ===\n")

    # Добавление константы
    print("3.1 Добавление 5000 к зарплате:")
    table.add('salary', 5000, result_column='salary_bonus')

    # Умножение
    print("\n3.2 Увеличение зарплаты на 10%:")
    table.mul('salary', 1.1, result_column='salary_inc')

    # Комбинированные операции
    print("\n3.3 Вычисление годового дохода (зарплата * 12):")
    table.mul('salary', 12, result_column='annual_salary')

    # Вычитание
    print("\n3.4 Разница между новой и старой зарплатой:")
    table.sub('salary_inc', 'salary', result_column='salary_diff')

    table.print_table()


def demo_comparison_operations(table):
    print("\n=== 4. ОПЕРАЦИИ СРАВНЕНИЯ ===\n")

    # Простые сравнения
    print("4.1 Зарплата > 60000:", table.gr('salary', 60000))
    print("4.2 Возраст < 30:", table.ls('age', 30))
    print("4.3 Активные сотрудники:", table.eq('is_active', True))

    # Сравнение столбцов
    print("\n4.4 Новая зарплата > старая зарплата:")
    print(table.gr('salary_inc', 'salary'))

    # Комбинированные условия
    print("\n4.5 Зарплата > 50000 И возраст < 30:")
    high_salary = table.gr('salary', 50000)
    young_age = table.ls('age', 30)
    combined_mask = [a and b for a, b in zip(high_salary, young_age)]
    print("Маска:", combined_mask)

    return high_salary, young_age


def demo_filtering(table, mask1, mask2):
    print("\n=== 5. ФИЛЬТРАЦИЯ ДАННЫХ ===\n")

    # Простая фильтрация
    print("5.1 Сотрудники с зарплатой > 60000:")
    t_high_salary = table.filter_rows(mask1, copy_table=True)
    t_high_salary.print_table()

    # Множественная фильтрация
    print("\n5.2 Молодые сотрудники (возраст < 30):")
    t_young = table.filter_rows(mask2, copy_table=True)
    t_young.print_table()

    # Комбинированная фильтрация
    print("\n5.3 Молодые сотрудники с высокой зарплатой:")
    combined_mask = [a and b for a, b in zip(mask1, mask2)]
    t_young_rich = table.filter_rows(combined_mask, copy_table=True)
    t_young_rich.print_table()


def demo_io_operations(table):
    print("\n=== 6. ОПЕРАЦИИ ВВОДА/ВЫВОДА ===\n")

    # Сохранение в CSV
    print("6.1 Сохранение в CSV...")
    save_csv(table, 'employees.csv')

    # Загрузка из CSV
    print("6.2 Загрузка из CSV...")
    t_csv = load_csv('employees.csv', auto_detect_types=True)
    print("Загруженная таблица:")
    t_csv.print_table()

    # Сохранение в Pickle
    print("\n6.3 Сохранение в Pickle...")
    save_pickle(table, 'employees.pkl')

    # Загрузка из Pickle
    print("6.4 Загрузка из Pickle...")
    t_pkl = load_pickle('employees.pkl')
    print("Загруженная таблица:")
    t_pkl.print_table()

    # Сохранение в текстовый формат
    print("\n6.5 Сохранение в текстовый файл...")
    save_text(table, 'employees.txt')
    print("Файл employees.txt создан!")

    return t_csv, t_pkl


def main():
    print("🚀 ИСПРАВЛЕННАЯ ДЕМОНСТРАЦИЯ ВОЗМОЖНОСТЕЙ ТАБЛИЧНОЙ СИСТЕМЫ\n")

    try:
        # 1. Базовые операции
        table = demo_basic_operations()

        # 2. Операции со строками
        demo_row_operations(table)

        # 3. Арифметические операции
        demo_arithmetic_operations(table)

        # 4. Операции сравнения
        mask1, mask2 = demo_comparison_operations(table)

        # 5. Фильтрация данных
        demo_filtering(table, mask1, mask2)

        # 6. Операции ввода/вывода
        demo_io_operations(table)

        print("\n🎉 ДЕМОНСТРАЦИЯ УСПЕШНО ЗАВЕРШЕНА!")
        print("\n📁 Созданные файлы: employees.csv, employees.pkl, employees.txt")

    except Exception as e:
        print(f"\n❌ Ошибка в демонстрации: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()