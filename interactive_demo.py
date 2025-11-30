# interactive_demo.py
from table import Table, TableError
from io_csv import load_table as load_csv, save_table as save_csv
from io_pickle import load_table as load_pickle, save_table as save_pickle
from io_text import save_table as save_text


class TableManager:
    def __init__(self):
        self.current_table = None

    def print_menu(self):
        print("\n" + "=" * 50)
        print("🎯 ИНТЕРАКТИВНЫЙ МЕНЕДЖЕР ТАБЛИЦ")
        print("=" * 50)

        if self.current_table:
            print(
                f"📊 Текущая таблица: {len(self.current_table.rows)} строк, {len(self.current_table.columns)} столбцов")
        else:
            print("📊 Текущая таблица: НЕТ")

        print("\n1. 📝 Создать новую таблицу")
        print("2. 📂 Загрузить таблицу из файла")
        print("3. 👀 Просмотреть таблицу")
        print("4. 🔧 Установить типы данных")
        print("5. ➕ Арифметические операции")
        print("6. 🔍 Фильтрация данных")
        print("7. 📊 Анализ данных")
        print("8. 💾 Сохранить таблицу")
        print("9. 📋 Примеры таблиц")
        print("0. ❌ Выход")
        print("-" * 50)

    def get_choice(self):
        try:
            choice = input("Выберите действие (0-9): ").strip()
            return int(choice)
        except ValueError:
            print("❌ Ошибка: введите число от 0 до 9")
            return -1

    def wait_for_enter(self):
        input("\n↵ Нажмите Enter чтобы продолжить...")

    def create_table_interactive(self):
        print("\n📝 СОЗДАНИЕ НОВОЙ ТАБЛИЦЫ")
        print("-" * 30)

        # Ввод названий столбцов
        print("Введите названия столбцов через запятую:")
        print("Пример: Имя, Возраст, Зарплата, Активен")
        columns_input = input("Столбцы: ").strip()
        columns = [col.strip() for col in columns_input.split(',')]

        print(f"\nСозданы столбцы: {columns}")
        print("\nТеперь введите данные. Вводите строки по одной.")
        print("Формат: значения через запятую")
        print("Для завершения введите 'stop'")
        print("-" * 30)

        rows = []
        row_num = 1

        while True:
            row_input = input(f"Строка {row_num}: ").strip()
            if row_input.lower() == 'stop':
                break

            if row_input:
                row_data = [val.strip() for val in row_input.split(',')]
                if len(row_data) != len(columns):
                    print(f"❌ Ошибка: ожидается {len(columns)} значений, получено {len(row_data)}")
                    continue
                rows.append(row_data)
                row_num += 1

        if not rows:
            print("❌ Таблица не создана: нет данных")
            return

        try:
            self.current_table = Table(columns=columns, rows=rows)
            print(f"✅ Таблица создана успешно! {len(rows)} строк, {len(columns)} столбцов")
            self.current_table.print_table()
        except Exception as e:
            print(f"❌ Ошибка при создании таблицы: {e}")

    def load_table_interactive(self):
        print("\n📂 ЗАГРУЗКА ТАБЛИЦЫ")
        print("1. 📄 Загрузить из CSV")
        print("2. 💾 Загрузить из Pickle")
        print("0. ↩️ Назад")

        choice = self.get_choice()

        if choice == 0:
            return

        filename = input("Введите имя файла: ").strip()

        try:
            if choice == 1:
                self.current_table = load_csv(filename, auto_detect_types=True)
                print("✅ Таблица загружена из CSV")
            elif choice == 2:
                self.current_table = load_pickle(filename)
                print("✅ Таблица загружена из Pickle")
            else:
                print("❌ Неверный выбор")
                return

            self.current_table.print_table()

        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")

    def view_table(self):
        if not self.current_table:
            print("❌ Нет активной таблицы")
            return

        print("\n👀 ПРОСМОТР ТАБЛИЦЫ")
        print("-" * 30)
        self.current_table.print_table()

        print(f"\n📊 Информация:")
        print(f"   Строк: {len(self.current_table.rows)}")
        print(f"   Столбцов: {len(self.current_table.columns)}")
        print(f"   Столбцы: {', '.join(self.current_table.columns)}")

        if self.current_table.types:
            print(f"   Типы данных: {self.current_table.get_column_types(by_number=False)}")

    def set_types_interactive(self):
        if not self.current_table:
            print("❌ Нет активной таблицы")
            return

        print("\n🔧 УСТАНОВКА ТИПОВ ДАННЫХ")
        print("Доступные типы: int, float, bool, str")
        print("Текущие столбцы:", self.current_table.columns)
        print("-" * 30)

        types_dict = {}

        for col in self.current_table.columns:
            current_type = self.current_table._type_for(col).__name__
            print(f"\nСтолбец: {col} (текущий тип: {current_type})")
            print("Введите новый тип или нажмите Enter чтобы пропустить:")
            new_type = input("Тип: ").strip()

            if new_type and new_type in ['int', 'float', 'bool', 'str']:
                types_dict[col] = new_type
            elif new_type:
                print(f"❌ Неподдерживаемый тип: {new_type}")

        if types_dict:
            try:
                self.current_table.set_column_types(types_dict, by_number=False)
                print("✅ Типы данных установлены успешно!")
                print("Новые типы:", self.current_table.get_column_types(by_number=False))
            except Exception as e:
                print(f"❌ Ошибка установки типов: {e}")
        else:
            print("ℹ️ Типы не изменены")

    def arithmetic_operations(self):
        if not self.current_table:
            print("❌ Нет активной таблицы")
            return

        print("\n➕ АРИФМЕТИЧЕСКИЕ ОПЕРАЦИИ")
        print("Столбцы:", self.current_table.columns)
        print("-" * 30)

        print("1. ➕ Сложение")
        print("2. ➖ Вычитание")
        print("3. ✖️ Умножение")
        print("4. ➗ Деление")
        print("0. ↩️ Назад")

        choice = self.get_choice()
        if choice == 0:
            return

        operations = {
            1: ('add', '➕ СЛОЖЕНИЕ'),
            2: ('sub', '➖ ВЫЧИТАНИЕ'),
            3: ('mul', '✖️ УМНОЖЕНИЕ'),
            4: ('div', '➗ ДЕЛЕНИЕ')
        }

        if choice not in operations:
            print("❌ Неверный выбор")
            return

        op_name, op_display = operations[choice]

        print(f"\n{op_display}")
        col_a = input("Введите имя первого столбца: ").strip()

        print("Введите второй столбец ИЛИ число:")
        col_b_input = input("Столбец/число: ").strip()

        # Пытаемся определить, это число или имя столбца
        try:
            col_b = float(col_b_input)
            is_scalar = True
        except ValueError:
            col_b = col_b_input
            is_scalar = False

        result_col = input("Введите имя для нового столбца: ").strip()

        try:
            if op_name == 'add':
                self.current_table.add(col_a, col_b, result_column=result_col)
            elif op_name == 'sub':
                self.current_table.sub(col_a, col_b, result_column=result_col)
            elif op_name == 'mul':
                self.current_table.mul(col_a, col_b, result_column=result_col)
            elif op_name == 'div':
                self.current_table.div(col_a, col_b, result_column=result_col)

            print(f"✅ Операция выполнена успешно!")
            self.current_table.print_table()

        except Exception as e:
            print(f"❌ Ошибка операции: {e}")

    def filter_data_interactive(self):
        if not self.current_table:
            print("❌ Нет активной таблицы")
            return

        print("\n🔍 ФИЛЬТРАЦИЯ ДАННЫХ")
        print("Столбцы:", self.current_table.columns)
        print("-" * 30)

        print("1. 🟰 Равно (==)")
        print("2. ▶️ Больше (>)")
        print("3. ◀️ Меньше (<)")
        print("4. ▶️= Больше или равно (>=)")
        print("5. ◀️= Меньше или равно (<=)")
        print("6. ❌ Не равно (!=)")
        print("0. ↩️ Назад")

        choice = self.get_choice()
        if choice == 0:
            return

        operations = {
            1: ('eq', '🟰 РАВНО'),
            2: ('gr', '▶️ БОЛЬШЕ'),
            3: ('ls', '◀️ МЕНЬШЕ'),
            4: ('ge', '▶️= БОЛЬШЕ ИЛИ РАВНО'),
            5: ('le', '◀️= МЕНЬШЕ ИЛИ РАВНО'),
            6: ('ne', '❌ НЕ РАВНО')
        }

        if choice not in operations:
            print("❌ Неверный выбор")
            return

        op_name, op_display = operations[choice]

        print(f"\n{op_display}")
        column = input("Введите имя столбца: ").strip()

        print("Введите значение для сравнения:")
        value_input = input("Значение: ").strip()

        # Пытаемся преобразовать в число если возможно
        try:
            if '.' in value_input:
                value = float(value_input)
            else:
                value = int(value_input)
        except ValueError:
            value = value_input

        try:
            if op_name == 'eq':
                mask = self.current_table.eq(column, value)
            elif op_name == 'gr':
                mask = self.current_table.gr(column, value)
            elif op_name == 'ls':
                mask = self.current_table.ls(column, value)
            elif op_name == 'ge':
                mask = self.current_table.ge(column, value)
            elif op_name == 'le':
                mask = self.current_table.le(column, value)
            elif op_name == 'ne':
                mask = self.current_table.ne(column, value)

            filtered_table = self.current_table.filter_rows(mask, copy_table=True)

            print(f"✅ Найдено {len(filtered_table.rows)} строк:")
            filtered_table.print_table()

            save_choice = input("\n💾 Сохранить отфильтрованную таблицу? (y/n): ").strip().lower()
            if save_choice == 'y':
                filename = input("Введите имя файла: ").strip()
                save_csv(filtered_table, filename)
                print("✅ Таблица сохранена!")

        except Exception as e:
            print(f"❌ Ошибка фильтрации: {e}")

    def analyze_data(self):
        if not self.current_table:
            print("❌ Нет активной таблицы")
            return

        print("\n📊 АНАЛИЗ ДАННЫХ")
        print("-" * 30)

        numeric_columns = []
        for col in self.current_table.columns:
            try:
                values = self.current_table.get_values(col)
                # Проверяем, можно ли преобразовать в числа
                numeric_values = [v for v in values if v is not None and isinstance(v, (int, float))]
                if len(numeric_values) > 0:
                    numeric_columns.append(col)
            except:
                pass

        if not numeric_columns:
            print("ℹ️ Нет числовых столбцов для анализа")
            return

        print("Числовые столбцы:", numeric_columns)
        column = input("Выберите столбец для анализа: ").strip()

        if column not in numeric_columns:
            print("❌ Столбец не найден или не числовой")
            return

        try:
            values = self.current_table.get_values(column)
            numeric_values = [v for v in values if v is not None]

            if not numeric_values:
                print("❌ В столбце нет числовых данных")
                return

            print(f"\n📈 СТАТИСТИКА ПО СТОЛБЦУ '{column}':")
            print(f"   Количество значений: {len(numeric_values)}")
            print(f"   Минимальное: {min(numeric_values)}")
            print(f"   Максимальное: {max(numeric_values)}")
            print(f"   Среднее: {sum(numeric_values) / len(numeric_values):.2f}")
            print(f"   Сумма: {sum(numeric_values)}")

        except Exception as e:
            print(f"❌ Ошибка анализа: {e}")

    def save_table_interactive(self):
        if not self.current_table:
            print("❌ Нет активной таблицы")
            return

        print("\n💾 СОХРАНЕНИЕ ТАБЛИЦЫ")
        print("1. 📄 Сохранить в CSV")
        print("2. 💾 Сохранить в Pickle")
        print("3. 📝 Сохранить в текстовый формат")
        print("0. ↩️ Назад")

        choice = self.get_choice()
        if choice == 0:
            return

        filename = input("Введите имя файла: ").strip()

        try:
            if choice == 1:
                save_csv(self.current_table, filename)
                print("✅ Таблица сохранена в CSV")
            elif choice == 2:
                save_pickle(self.current_table, filename)
                print("✅ Таблица сохранена в Pickle")
            elif choice == 3:
                save_text(self.current_table, filename)
                print("✅ Таблица сохранена в текстовом формате")
            else:
                print("❌ Неверный выбор")

        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")

    def load_example_tables(self):
        print("\n📋 ПРИМЕРЫ ТАБЛИЦ")
        print("1. 👥 Сотрудники")
        print("2. 🏪 Продукты")
        print("3. 🎓 Студенты")
        print("0. ↩️ Назад")

        choice = self.get_choice()
        if choice == 0:
            return

        examples = {
            1: {
                'name': 'Сотрудники',
                'columns': ['Имя', 'Должность', 'Опыт_лет', 'Зарплата', 'На_испытании'],
                'rows': [
                    ['Алексей Петров', 'Разработчик', '3', '80000', 'False'],
                    ['Мария Иванова', 'Дизайнер', '1', '60000', 'True'],
                    ['Дмитрий Сидоров', 'Менеджер', '5', '95000', 'False'],
                    ['Ольга Козлова', 'Аналитик', '2', '70000', 'True']
                ],
                'types': {'Опыт_лет': 'int', 'Зарплата': 'int', 'На_испытании': 'bool'}
            },
            2: {
                'name': 'Продукты',
                'columns': ['Товар', 'Цена', 'Количество', 'Скидка'],
                'rows': [
                    ['Ноутбук', '999.99', '5', '0.1'],
                    ['Мышь', '25.50', '20', '0.05'],
                    ['Клавиатура', '75.00', '15', '0.0'],
                    ['Монитор', '299.99', '8', '0.15']
                ],
                'types': {'Цена': 'float', 'Количество': 'int', 'Скидка': 'float'}
            },
            3: {
                'name': 'Студенты',
                'columns': ['ФИО', 'Класс', 'Математика', 'Физика', 'Химия', 'Отличник'],
                'rows': [
                    ['Иванов А.Б.', '10А', '85', '90', '88', 'True'],
                    ['Петрова В.Г.', '10Б', '92', '95', '96', 'True'],
                    ['Сидоров Д.Е.', '10А', '78', '65', '72', 'False'],
                    ['Козлова Ж.З.', '10Б', '88', '92', '85', 'True']
                ],
                'types': {'Математика': 'int', 'Физика': 'int', 'Химия': 'int', 'Отличник': 'bool'}
            }
        }

        if choice in examples:
            example = examples[choice]
            self.current_table = Table(
                columns=example['columns'],
                rows=example['rows']
            )
            self.current_table.set_column_types(example['types'], by_number=False)
            print(f"✅ Загружен пример: {example['name']}")
            self.current_table.print_table()
        else:
            print("❌ Неверный выбор")

    def run(self):
        print("🚀 Добро пожаловать в интерактивный менеджер таблиц!")
        print("Создавайте, анализируйте и сохраняйте таблицы легко!")

        while True:
            self.print_menu()
            choice = self.get_choice()

            if choice == 0:
                print("\n👋 До свидания!")
                break
            elif choice == 1:
                self.create_table_interactive()
            elif choice == 2:
                self.load_table_interactive()
            elif choice == 3:
                self.view_table()
            elif choice == 4:
                self.set_types_interactive()
            elif choice == 5:
                self.arithmetic_operations()
            elif choice == 6:
                self.filter_data_interactive()
            elif choice == 7:
                self.analyze_data()
            elif choice == 8:
                self.save_table_interactive()
            elif choice == 9:
                self.load_example_tables()
            else:
                print("❌ Неверный выбор, попробуйте снова")

            self.wait_for_enter()


def main():
    manager = TableManager()
    manager.run()


if __name__ == '__main__':
    main()