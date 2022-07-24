import scrapy


class SanshaoSpider(scrapy.Spider):
    name = 'sanshao'
    allowed_domains = ['tj1024.com']
    start_urls = ['https://www.tj1024.com/shenyinwangzuo/']

    def parse(self, response):
        contents = response.xpath("//dd/a/@href")
        for content in contents:
            link = content.get()
            next_url = f"https://www.tj1024.com/shenyinwangzuo/{link}"
            yield scrapy.Request(next_url, self.parse_content, meta={"index": contents.index(content)})


    def parse_content(self, response):
        title = response.xpath("//h1/text()").get()
        content_list = response.xpath('//*[@id="main"]/div[2]/p/text()')
        result = []
        for l in content_list:
            result.append(l.get().strip())
        content = "\n".join(result)

        yield {
            "index": response.meta.get("index"),
            "chapter": title,
            "content": content
        }
        print(title)