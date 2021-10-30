# -*- coding: utf-8 -*-
import scrapy


class RanwenSpider(scrapy.Spider):
    name = 'kuiba'
    allowed_domains = ['99csw.com']
    start_urls = ['https://www.99csw.com/book/4882/index.htm']

    def parse(self, response):
        contents = response.xpath("//dl[@id='dir']/dd/a/@href")
        for content in contents:
            link = content.get()
            next_url = f"https://www.99csw.com{link}"
            print(next_url)
            yield scrapy.Request(next_url, self.parse_content, meta={"index": contents.index(content)})
            return

    def parse_content(self, response):
        titles = response.xpath("//div[@id='content']//h2/text()")
        title = titles[0].get() + " " + titles[1].get()
        return
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
