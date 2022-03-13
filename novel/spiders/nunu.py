# -*- coding: utf-8 -*-
import scrapy


class RanwenSpider(scrapy.Spider):
    name = 'nunu'
    allowed_domains = ['kanunu8.com']
    start_urls = ['https://www.kanunu8.com/book4/10522/index.html'] # 背叛

    def parse(self, response):
        contents = response.xpath("//table[@cellpadding='7']//a")
        for content in contents:
            link = content.xpath("./@href").get()
            next_url = response.urljoin(link)
            yield scrapy.Request(next_url, self.parse_content, meta={"index": contents.index(content)})

    def parse_content(self, response):
        title = response.xpath("//h2/font/text()").get()
        content_list = response.xpath("//p/text()")
        content = ""
        for p in content_list:
            content += p.get().replace(" ","") + "\n"
        yield {
            "index": response.meta.get("index"),
            "chapter": title,
            "content": content
        }
        print(title)
