from parser import book_url_parser, main_parser
from db_config import insert_into_db, create_table, create_table_urls, insert_into_db_page_url

def main():
    table_name = "products"
    page_url_table = "page_urls"

    urls_data = book_url_parser()

    # create_table_urls(page_url_table)
    # insert_into_db_page_url(page_url_table, urls_data)

    abstract_data = main_parser(page_url_table)
    create_table(table_name, abstract_data)
    insert_into_db(table_name, abstract_data)

if __name__ == "__main__":
    main()