# -*- coding: utf-8 -*-
import scrapy


class RanwenSpider(scrapy.Spider):
    name = 'aikan'
    allowed_domains = ['bqg121.com']
    start_urls = ['https://m.bqg121.com/info/16028/list.html'] # 重生唐三

    def parse(self, response):
        contents = response.xpath("//dd/a")
        for content in contents[1:]:
            title = content.xpath("./text()").get()
            link = content.xpath("./@href").get()
            next_url = f"https://m.bqg121.com{link}"
            yield scrapy.Request(next_url, self.parse_content, meta={"index": contents.index(content),"title" : title})

    def parse_content(self, response):
        raw_content = response.xpath('//div[@id="chaptercontent"]').get()

        content = raw_content\
            .replace("<br>","\n",-1)
        content = "\n".join(content.split("\n")[1:-2])

        title = response.meta.get("title")
        current_url = response.url
        is_first_page = "_" not in current_url
        next_link = response.xpath('//div[@class="Readpage pagedown"]/a[@id="pb_next"]')
        has_next_page = next_link is not None and "_" in next_link.xpath("./@href").get()

        if not is_first_page:
            pre_content = response.meta.get("content")
            content = pre_content.strip() + content.strip()

        if has_next_page:
            next_url = f"https://m.bqg121.com{next_link.xpath('./@href').get()}"
            yield scrapy.Request(next_url, self.parse_content, meta={"index": response.meta.get("index"),"content": content,"title": title})
        else:
            yield {
                "index": response.meta.get("index"),
                "chapter": response.meta.get("title"),
                "content": content
            }
            print(response.meta.get("title"))

