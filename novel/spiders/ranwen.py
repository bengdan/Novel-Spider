# -*- coding: utf-8 -*-
import scrapy


class RanwenSpider(scrapy.Spider):
    name = 'ranwen'
    allowed_domains = ['ranwen.la']
    # start_urls = ['https://www.ranwen.la/files/article/153/153252/'] # 万相之王
#    start_urls = ['https://www.ranwen.la/files/article/14/14868/'] # 雪中悍刀行
    start_urls = ['https://www.ranwen.la/files/article/157/157409/'] # 斗罗大陆
#    start_urls = ['https://www.ranwen.la/files/article/93/93879/'] # 三寸人间
#    start_urls = ['https://www.ranwen.la/files/article/99/99829/'] # 大梦主
    # start_urls = ['https://www.ranwen.la/files/article/93/93724/'] # 剑来
#    start_urls = ['https://www.ranwen.la/files/article/133/133102/'] # 开端

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
            if ".com" in p.get():
                continue
            content += p.get() + "\n"

        yield {
            "index": response.meta.get("index"),
            "chapter": title,
            "content": content
        }
        print(title)
