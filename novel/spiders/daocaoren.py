# -*- coding: utf-8 -*-
import scrapy


class DaocaorenSpider(scrapy.Spider):
    name = 'daocaoren'
    allowed_domains = ['www.20dcr.com']
    start_urls = ['https://www.20dcr.com/book/4564/1105393.html']

    def parse(self, response):
        title = response.xpath("//h1//text()").get()
        content_list = response.xpath("//div[@id='cont-text']//p/text()")
        content = ""
        for p in content_list:
            content += p.get() + "\n"
        if self.has_next_page(response):
            next_url_path = response.xpath("//div[@class='row']//a[3]/@href").get()
            next_url = f"https://www.20dcr.com{next_url_path}"
            raw_title = response.request.meta.get("title")
            if raw_title:
                title = response.request.meta.get("title")
                content = response.request.meta.get("content") + "\n" + content
            yield scrapy.Request(next_url, self.parse,meta={
                "title":title,
                "content": content
            })
        else:
            raw_title = response.request.meta.get("title")
            if raw_title:
                title = raw_title
                content = response.request.meta.get("content") + "\n" + content
            next_url_path = response.xpath("//div[@class='row']//a[3]/@href").get()
            next_url = f"https://www.20dcr.com{next_url_path}"
            yield {
                "chapter": title,
                "content":content
            }
            print(title)
            yield scrapy.Request(next_url,self.parse)

    @staticmethod
    def has_next_page(response):
        buttons = response.xpath("//button/text()")
        for b in buttons:
            if "下一页" in b.get():
                return True
        return False
