# -*- coding: utf-8 -*-
import scrapy


class RanwenSpider(scrapy.Spider):
    name = 'aikan'
    allowed_domains = ['ixs.la']
    start_urls = ['https://www.ixs.la/ks77009/'] # 重生唐三

    def parse(self, response):
        contents = response.xpath("//dd/a/@href")
        for content in contents[12:]:
            link = content.get()
            next_url = f"https://www.ixs.la{link}"
            yield scrapy.Request(next_url, self.parse_content, meta={"index": contents.index(content)})

    def parse_content(self, response):
        title = response.xpath("//h1/text()").get()
        raw_content = response.xpath("//div[@id='content']").get()
        content = raw_content\
            .replace(";&nbsp;","",-1)\
            .replace("&nbsp","",-1)\
            .replace(" ","",-1)\
            .replace("<br />","\n",-1)\
            .replace("<br>","\n",-1)\
            .replace("&emsp;","\n",-1)\
            .replace("</div>","",-1)\
            .replace('<div id="content">',"",-1)

        yield {
            "index": response.meta.get("index"),
            "chapter": title,
            "content": content
        }
        print(title)
