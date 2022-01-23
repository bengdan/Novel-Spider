# -*- coding: utf-8 -*-
import scrapy


class DaocaorenSpider(scrapy.Spider):
    name = 'daocaoren'
    allowed_domains = ['www.20dcr.com']
    start_urls = ['https://www.20dcr.com/writer/']

    def parse(self, response):
        author_list = response.xpath("""//div[@class="col-md-2 col-sm-2 col-xs-4 b10"]""")
        for author_div in author_list:
            author_name = author_div.xpath("./h3/a/text()").get()
            link = author_div.xpath("./h3/a/@href").get()
            print(f"author : {author_name} {response.urljoin(link)}")
            yield scrapy.Request(response.urljoin(link),self.parse_author)
        pagination = response.xpath("//div[@class='page']//li/a")
        last_page = pagination[-1]
        if "下页" in last_page.xpath("./text()").get():
            next_page = last_page.xpath("./@href").get()
            print(f"next author page : {response.urljoin(next_page)}")
            yield scrapy.Request(response.urljoin(next_page),self.parse)

    def parse_author(self,response):
        # author info
        author_info = response.xpath("//div[@class='book-info']")
        avatar = author_info.xpath(".//img/@src").get()
        avatar_link = response.urljoin(avatar)
        name = author_info.xpath(".//h1/a/text()").get()
        intro = author_info.xpath(".//p/text()").get()

        # book list
        book_list = response.xpath("//div[@class='col-md-12 mb10']")
        for book in book_list:
            book_title = book.xpath(".//h4/a/text()").get()
            book_link = response.urljoin(book.xpath(".//h4/a/@href").get())
            print(f"Parsing book : {book_link}")
            # yield scrapy.Request(book_link,self.parse_book)
            yield {
            "title":book_title,
                "link":book_link
            }

    def parse_book(self,response):
        # book info
        book_info = response.xpath("//div[@class='book-info']")
        book_img = response.urljoin(book_info.xpath(".//img/@src").get())
        print(book_img)
        pass