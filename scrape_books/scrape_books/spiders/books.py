from typing import Generator

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response) -> Generator:
        for book in response.css(".product_pod"):
            href_to_book_detail_page = book.css("h3 a::attr(href)").get()
            absolut_url_to_book_detail_page = response.urljoin(
                href_to_book_detail_page
            )
            yield scrapy.Request(
                absolut_url_to_book_detail_page,
                callback=self.parse_sengle_book
            )


        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_sengle_book(self, response: Response) -> Generator:
        yield {
            "title": response.css("h1::text").get(),
            "price": response.css(
                ".price_color::text"
            ).get().replace("£", ""),
            "amount_in_stock": "".join(
                [i for i in str(
                    response.css(
                        ".instock.availability::text"
                    ).getall()
                ) if i.isnumeric()]
            ),
            "rating": response.css(
                ".star-rating::attr(class)"
            ).get().split()[-1],
            "description": response.css("h2::text").get(),
            "category": response.css(
                ".breadcrumb li:nth-last-child(2) a::text"
            ).get(),
            "upc": response.xpath(
                "//th[text()='UPC']/following-sibling::td/text()"
            ).get(),
        }
