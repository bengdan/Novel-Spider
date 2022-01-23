# -*- coding: utf-8 -*-
import scrapy


class RanwenSpider(scrapy.Spider):
    name = 'piaoxiang'
    allowed_domains = ['ptwxz.com']
    start_urls = ['https://www.ptwxz.com/html/11/11934/'] # 金刚不坏大寨主

    def parse(self, response):
        contents = response.xpath("//ul//a/@href")
        for content in contents:
            link = content.get()
            next_url = f"{self.start_urls[0]}{link}"
            yield scrapy.Request(next_url, self.parse_content, meta={"index": contents.index(content)})

    def parse_content(self, response):
        title = response.xpath("//h1/text()").get()
        raw_content = response.text.split("</table>\r\n\r\n\r\n")[1].split("<!-- 翻页上AD开始")[0]

        content = raw_content\
            .replace(";&nbsp;","",-1)\
            .replace("&nbsp","",-1)\
            .replace("<br />","\n",-1)\
            .replace("<br>","\n",-1)\
            .replace("&emsp;","\n",-1)\
            .replace("</div>","",-1)

        yield {
            "index": response.meta.get("index"),
            "chapter": title,
            "content": content
        }
        print(title)
