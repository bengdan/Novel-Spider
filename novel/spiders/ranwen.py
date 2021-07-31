# -*- coding: utf-8 -*-
import scrapy


class RanwenSpider(scrapy.Spider):
    name = 'ranwen'
    allowed_domains = ['ranwen.la']
    start_urls = ['https://www.ranwen.la/files/article/119/119795/1331051.html']

    def parse(self, response):
        title = response.xpath("//h1//text()").get()
        content_list = response.xpath("//div[@id='content']//p/text()")
        content = ""
        for p in content_list:
            content += p.get() + "\n"

        next_url_path = response.xpath("//div[@class='bottem1']//a[3]/@href").get()
        next_url = f"https://www.ranwen.la{next_url_path}"
        yield {
            "chapter": title,
            "content": content
        }
        print(title)
        yield scrapy.Request(next_url, self.parse)
