# -*- coding: utf-8 -*-
import scrapy


class PiaoxiangSpider(scrapy.Spider):
    name = 'piaoxiang'
    allowed_domains = ['piaotian.com']
    # start_urls = ['https://www.ptwxz.com/html/0/727/index.html'] # 神印王座
    # start_urls = ['https://www.piaotian.com/html/1/1272/index.html'] # 神印王座
    start_urls = ['https://www.piaotian.com/html/8/8146/index.html'] # 神印王座
    # start_urls = ['https://www.ptwxz.com/html/11/11934/'] # 金刚不坏大寨主

    def parse(self, response):
        contents = response.xpath("//ul//a/@href")
        for content in contents:
            link = content.get()
            next_url = f"{self.start_urls[0][:-10]}{link}"
            yield scrapy.Request(next_url, self.parse_content, meta={"index": contents.index(content)})

    def parse_content(self, response):
        title = response.xpath("//h1/text()").get()
        raw_content = response.text.split('<center><script language="javascript" src="/scripts/read/style2.js"></script></center>')
        raw_content = raw_content[0].split("""</table></td>\n</tr></table>\n<br>\n&nbsp;&nbsp;&nbsp;&nbsp;""")[1]

        content = raw_content\
            .replace(";&nbsp;","",-1)\
            .replace("&nbsp","",-1)\
            .replace("<br />","\n",-1)\
            .replace("<br>","\n",-1)\
            .replace("<br/><br/>","\n",-1)\
            .replace("&emsp;","\n",-1)\
            .replace("</div>","",-1)

        yield {
            "index": response.meta.get("index"),
            "chapter": title,
            "content": content
        }
        print(title)
