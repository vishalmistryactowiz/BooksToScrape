PATHS = {
    "loop_xpath": '//article[@class="product_pod"]',
    "title": './/h3/a/@title',
    "Product_url" : './/div[@class="image_container"]/a/@href',
    "image_path": './/div[@class="image_container"]/a/img/@src',
    "price_path": './/p[@class="price_color"]/text()',
    "rating_path": ".//p[contains(@class, 'star-rating')]/@class",
    "stock_path": './/p[contains(@class, "instock")]/text()',

    "upc": '//table//tr[th[text()="UPC"]]/td/text()',
    "product_type": '//table//tr[th[text()="Product Type"]]/td/text()',
    "price_excl_tax": '//table//tr[th[text()="Price (excl. tax)"]]/td/text()',
    "price_incl_tax": '//table//tr[th[text()="Price (incl. tax)"]]/td/text()',
    "tax": '//table//tr[th[text()="Tax"]]/td/text()',
    "availability_detail": '//table//tr[th[text()="Availability"]]/td/text()',
    "description": '//div[@id="product_description"]/following-sibling::p[1]/text()',
    "category": '(//ul[@class="breadcrumb"]/li/a/text())[3]',
    "star_rating": '//p[contains(@class,"star-rating")]/@class'
}