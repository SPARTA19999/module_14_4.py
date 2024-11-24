import sqlite3


def initiate_db():
    """
    Инициализирует базу данных и создаёт таблицу Products, если она ещё не создана.
    """
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            image_path TEXT  -- Добавляем столбец image_path
        )
    """)
    connection.commit()
    connection.close()


def add_image_path_column():
    """
    Добавляет столбец image_path, если он ещё не существует.
    """
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    try:
        cursor.execute("ALTER TABLE Products ADD COLUMN image_path TEXT")
        connection.commit()
    except sqlite3.OperationalError:
        # Этот столбец уже добавлен
        pass
    connection.close()


def get_all_products():
    """
    Возвращает все записи из таблицы Products.
    """
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id, title, description, price, image_path FROM Products")
    products = cursor.fetchall()
    connection.close()
    return products


def insert_sample_products():
    """
    Заполняет таблицу Products тестовыми данными, если она пуста.
    """
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Products")
    count = cursor.fetchone()[0]
    if count == 0:
        products = [
            ("Product1", "Описание продукта 1", 100, "images/product1.jpg"),
            ("Product2", "Описание продукта 2", 200, "images/product2.jpg"),
            ("Product3", "Описание продукта 3", 300, "images/product3.jpg"),
            ("Product4", "Описание продукта 4", 400, "images/product4.jpg")
        ]
        cursor.executemany("INSERT INTO Products (title, description, price, image_path) VALUES (?, ?, ?, ?)", products)
        connection.commit()
        print("Тестовые данные добавлены.")
    else:
        print(f"Таблица уже содержит данные: {count} записей.")
    connection.close()


def debug_db(table_name="Products"):
    """
    Проверяет содержимое указанной таблицы.
    """
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    if rows:
        print(f"Содержимое таблицы {table_name}:")
        for row in rows:
            print(row)
    else:
        print(f"Таблица {table_name} пуста.")
    connection.close()


if __name__ == "__main__":
    # Инициализация базы данных
    initiate_db()

    # Вставка тестовых данных, если таблица пуста
    insert_sample_products()

    # Проверка содержимого таблицы Products
    debug_db()  # Проверка содержимого таблицы Products

    # Дополнительно можно получить все продукты и вывести их
    products = get_all_products()
    print("Все продукты:")
    for product in products:
        print(product)
