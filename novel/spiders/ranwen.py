# -*- coding: utf-8 -*-
import scrapy


class RanwenSpider(scrapy.Spider):
    name = 'ranwen'
    allowed_domains = ['ranwen.la']
    # start_urls = ['https://www.ranwen.la/files/article/96/96954/'] # 圣墟
    start_urls = ['https://www.ranwen.la/files/article/157/157409/'] # 斗罗大陆
    # start_urls = ['https://www.ranwen.la/files/article/3/3529/'] # 冰火魔厨
    # start_urls = ['https://www.ranwen.la/files/article/162/162120/']
    # start_urls = ['https://www.ranwen.la/files/article/93/93724/'] # 剑来

    def parse(self, response):
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
            content += p.get() + "\n"

        yield {
            "index": response.meta.get("index"),
            "chapter": title,
            "content": content
        }
        print(title)
