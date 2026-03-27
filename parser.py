from lxml import html
import json
import os
import threading
import requests
from x_paths import PATHS
from db_config import fetch_page_urls_one_by_one, update_page_status,fetch_product_urls,update_product_details

def read_data(file):
    with open(file, "r", encoding="utf-8") as f:
        tree = html.fromstring(f.read())
        return tree

def book_data_parser(url_fetch, folder_name, store_list, lock, table_name):
    try:
        res = requests.get(url_fetch)
        res.encoding = "utf-8"

        page_name = url_fetch.rstrip('/').split('/')[-1].replace('.html', '')
        file_path = os.path.join(folder_name, f"{page_name}.html.gz")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(res.text)

        data = html.fromstring(res.text)
        books = data.xpath(PATHS["loop_xpath"])
        book_list = []

        for book in books:
            title = book.xpath(PATHS["title"])
            product_url = book.xpath(PATHS["Product_url"])
            img_url = book.xpath(PATHS["image_path"])
            price = book.xpath(PATHS["price_path"])
            stock = book.xpath(PATHS["stock_path"])

            store_dict = {
                "Title": title[0].strip() if title else "",
                "Product_url": "https://books.toscrape.com/catalogue/" + product_url[0].strip() if product_url else "",
                "Img_url": "https://books.toscrape.com/" + img_url[0].strip() if img_url else "",
                "Price": price[0].strip() if price else "",
                "Stock": "".join(stock).strip() if stock else "",
            }
            book_list.append(store_dict)
            

        with lock:
            store_list.extend(book_list)

        update_page_status(table_name, url_fetch, "complete")

    except Exception as e:
        print(f"Request Failed: {url_fetch} | {e}")

def book_url_parser():
    page_list = []
    base_url = "https://books.toscrape.com/catalogue/"
    current_url = "https://books.toscrape.com/catalogue/page-1.html"

    while True:
        response = requests.get(current_url)
        tree = html.fromstring(response.text)

        page_list.append({
            "page_url": current_url
        })

        next_page = tree.xpath('//li[@class="next"]/a/@href')

        if not next_page:
            break

        current_url = base_url + next_page[0]

    return page_list

def main_parser(page_urls):
    urls_fetch = list(fetch_page_urls_one_by_one(page_urls))
    store_list = []
    folder_name = r"D:\Vishal Mistry\bookstoscrape_files"
    os.makedirs(folder_name, exist_ok=True)
    lock = threading.Lock()
    batch_size = 10

    for i in range(0, len(urls_fetch), batch_size):
        batch = urls_fetch[i:i + batch_size]
        threads = []

        for url_fetch in batch:
            t = threading.Thread(
                target=book_data_parser,
                args=(url_fetch, folder_name, store_list, lock, page_urls)
            )
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

    return store_list

def parse_product_detail(product_url, table_name):
    try:
        res = requests.get(product_url, timeout=20)
        res.encoding = "utf-8"
        tree = html.fromstring(res.text)

        upc = tree.xpath(PATHS["upc"])
        product_type = tree.xpath(PATHS["product_type"])
        price_excl_tax = tree.xpath(PATHS["price_excl_tax"])
        price_incl_tax = tree.xpath(PATHS["price_incl_tax"])
        tax = tree.xpath(PATHS["tax"])
        availability = tree.xpath(PATHS["availability_detail"])
        description = tree.xpath(PATHS["description"])
        category = tree.xpath(PATHS["category"])
        star_rating = tree.xpath(PATHS["star_rating"])

        rating_value = ""
        if star_rating:
            # example class => "star-rating Three"
            parts = star_rating[0].split()
            if len(parts) > 1:
                rating_value = parts[-1]

        detail_data = {
            "upc": upc[0].strip() if upc else "",
            "product_type": product_type[0].strip() if product_type else "",
            "price_excl_tax": price_excl_tax[0].strip() if price_excl_tax else "",
            "price_incl_tax": price_incl_tax[0].strip() if price_incl_tax else "",
            "tax": tax[0].strip() if tax else "",
            "availability": availability[0].strip() if availability else "",
            "description": description[0].strip() if description else "",
            "category": category[0].strip() if category else "",
            "star_rating": rating_value,
        }

        update_product_details(table_name, product_url, detail_data)

    except Exception as e:
        print(f"Detail parse failed: {product_url} | {e}")

def update_old_table_from_product_urls(table_name):
    product_urls = list(fetch_product_urls(table_name))
    batch_size = 10

    for i in range(0, len(product_urls), batch_size):
        batch = product_urls[i:i + batch_size]
        threads = []

        for product_url in batch:
            t = threading.Thread(
                target=parse_product_detail,
                args=(product_url, table_name)
            )
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

def write_data(store_data):
    with open("Book.json", "w", encoding="utf-8") as f:
        json.dump(store_data, f, indent=4, ensure_ascii=False)