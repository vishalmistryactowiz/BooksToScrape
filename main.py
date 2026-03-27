from parser import book_url_parser, main_parser,update_old_table_from_product_urls
from db_config import insert_into_db, create_table_product, create_table_urls, insert_into_db_page_url,add_columns_if_not_exists

def main():
    table_name = "products"
    page_url_table = "page_urls"

    urls_data = book_url_parser()

    create_table_urls(page_url_table)
    insert_into_db_page_url(page_url_table, urls_data)

    abstract_data = main_parser(page_url_table)
    create_table_product(table_name, abstract_data)
    insert_into_db(table_name, abstract_data)

    add_columns_if_not_exists(table_name)
    update_old_table_from_product_urls(table_name)

if __name__ == "__main__":
    main()