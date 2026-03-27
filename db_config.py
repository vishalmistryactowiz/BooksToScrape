import mysql.connector

def make_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="actowiz",
        database="booktoscrape"
    )
    return conn

def create_table_product(table_name: str, rows: list[dict]):
    if not rows:
        return

    cols = []
    for col, val in rows[0].items():
        if isinstance(val, int):
            dtype = "INT"
        elif isinstance(val, float):
            dtype = "FLOAT"
        elif isinstance(val, bool):
            dtype = "BOOLEAN"
        else:
            dtype = "VARCHAR(255)"
        cols.append(f"`{col}` {dtype}")

    columns_query = ",".join(cols)

    q = f"""
    CREATE TABLE IF NOT EXISTS `{table_name}` (
        {columns_query}
    )
    """

    conn = make_connection()
    cursor = conn.cursor()
    cursor.execute(q)
    conn.commit()
    cursor.close()
    conn.close()

def create_table_urls(table_name: str):
    q = f"""
    CREATE TABLE IF NOT EXISTS `{table_name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        page_url VARCHAR(255) NOT NULL UNIQUE,
        status VARCHAR(50) NOT NULL DEFAULT 'pending'
    )
    """

    conn = make_connection()
    cursor = conn.cursor()
    cursor.execute(q)
    conn.commit()
    cursor.close()
    conn.close()

def insert_into_db(table_name: str, rows: list[dict]):
    if not rows:
        return

    cols = ",".join([f"`{col}`" for col in rows[0].keys()])
    vals = ",".join(["%s"] * len(rows[0].keys()))
    q = f"INSERT IGNORE INTO `{table_name}` ({cols}) VALUES ({vals})"

    conn = make_connection()
    cursor = conn.cursor()
    cursor.executemany(q, [tuple(r.values()) for r in rows])
    conn.commit()
    cursor.close()
    conn.close()

def insert_into_db_page_url(table_name: str, rows: list[dict]):
    if not rows:
        return

    q = f"""
    INSERT IGNORE INTO `{table_name}` (page_url)
    VALUES (%s)
    """

    data = [(row["page_url"],) for row in rows]

    conn = make_connection()
    cursor = conn.cursor()
    cursor.executemany(q, data)
    conn.commit()
    cursor.close()
    conn.close()

def fetch_page_urls_one_by_one(table_name: str):
    conn = make_connection()
    cursor = conn.cursor(dictionary=True)

    q = f"SELECT page_url FROM `{table_name}` WHERE status = 'pending'"
    cursor.execute(q)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    for row in rows:
        yield row["page_url"]

def update_page_status(table_name: str, page_url: str, status: str):
    conn = make_connection()
    cursor = conn.cursor()

    q = f"UPDATE `{table_name}` SET status = %s WHERE page_url = %s"
    cursor.execute(q, (status, page_url))

    conn.commit()
    cursor.close()
    conn.close()

def add_columns_if_not_exists(table_name: str):
    queries = [
        f"ALTER TABLE `{table_name}` ADD COLUMN `upc` VARCHAR(255)",
        f"ALTER TABLE `{table_name}` ADD COLUMN `product_type` VARCHAR(255)",
        f"ALTER TABLE `{table_name}` ADD COLUMN `price_excl_tax` VARCHAR(255)",
        f"ALTER TABLE `{table_name}` ADD COLUMN `price_incl_tax` VARCHAR(255)",
        f"ALTER TABLE `{table_name}` ADD COLUMN `tax` VARCHAR(255)",
        f"ALTER TABLE `{table_name}` ADD COLUMN `availability` VARCHAR(255)",
        f"ALTER TABLE `{table_name}` ADD COLUMN `description` TEXT",
        f"ALTER TABLE `{table_name}` ADD COLUMN `category` VARCHAR(255)",
        f"ALTER TABLE `{table_name}` ADD COLUMN `star_rating` VARCHAR(50)"
    ]

    conn = make_connection()
    cursor = conn.cursor()

    for q in queries:
        try:
            cursor.execute(q)
        except mysql.connector.Error:
            pass

    conn.commit()
    cursor.close()
    conn.close()

def fetch_product_urls(table_name: str):
    conn = make_connection()
    cursor = conn.cursor(dictionary=True)

    q = f"""
    SELECT product_url
    FROM `{table_name}`
    WHERE product_url IS NOT NULL AND product_url != ''
    """
    cursor.execute(q)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    for row in rows:
        yield row["product_url"]

def update_product_details(table_name: str, product_url: str, data: dict):
    conn = make_connection()
    cursor = conn.cursor()

    q = f"""
    UPDATE `{table_name}`
    SET
        upc = %s,
        product_type = %s,
        price_excl_tax = %s,
        price_incl_tax = %s,
        tax = %s,
        availability = %s,
        description = %s,
        category = %s,
        star_rating = %s
    WHERE product_url = %s
    """

    values = (
        data.get("upc", ""),
        data.get("product_type", ""),
        data.get("price_excl_tax", ""),
        data.get("price_incl_tax", ""),
        data.get("tax", ""),
        data.get("availability", ""),
        data.get("description", ""),
        data.get("category", ""),
        data.get("star_rating", ""),
        product_url
    )

    cursor.execute(q, values)
    conn.commit()
    cursor.close()
    conn.close()
