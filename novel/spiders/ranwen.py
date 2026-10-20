# -*- coding: utf-8 -*-
import scrapy


class RanwenSpider(scrapy.Spider):
    name = 'ranwen'
    allowed_domains = ['ranwen.la']
    start_urls = ['https://www.ranwen.la/files/article/19/19246/'] # 斗罗大陆 2


    def parse(self, response):
        print("parse")
        print(response.status)
        contents = response.xpath("//dd/a")
        for content in contents[15:]:
            link = content.xpath("./@href").get()
            next_url = f"https://www.ranwen.la{link}"
            yield scrapy.Request(next_url, self.parse_content, meta={"index": contents.index(content)})

    def parse_content(self, response):
        title = response.xpath("//h1//text()").get()

        content_list = response.xpath("//div[@id='content']//p/text()")
        content = ""
        for p in content_list:
            if ".com" in p.get() or "www" in p.get():
                continue
            if "第" in p.get() and "章" in p.get():
                continue
            content += p.get() + "\n"

        yield {
            "index": response.meta.get("index"),
            "chapter": title,
            "content": content
        }
        print(title)
