import base64
import csv
import os
import re
import scrapy

csv.field_size_limit(2**31 - 1)


class HetushuSpider(scrapy.Spider):
    name = "hetushu"
    allowed_domains = ["hetushu.com"]
    start_urls = ["https://www.hetushu.com/book/10195/index.html"]
    csv_path = "data.csv"

    # 粘贴你复制过来的原始 Cookie 字符串
    raw_cookie = (
        "_ga=GA1.1.1409458712.1792463328; "
        "cf_clearance=Iz0SVSbwMupgQaddFccwr3Vccq0zMWtYfdslYaXa9ic-1792479331-1.2.1.1-6ijIDDniMY95u9O17onkmbjSEwtmZZEUS_cLrS1RHXRMrLIrRlNAp2MSy_wcIQec0ep6gofaIv_b5JE.b54YTxi1W.mX7Z9Tr6sbc6DLq4twB8vlw86ocv1P3NUAfa_zc96FX8tF59Knp1pqzy_PQxObw9_fd2bdp_ftZAYe2T2kcWLdpni1bo1iZHOUU6wt1CkT652PzX63Lu7MNljSU8d_dZPVtkQrycYw1XhZnKhuHGa63oK3UZm57oyrUn2QtaBCbM1L9uq1YXB953zvAUlexorrUvqt1QTHeCpK3jvqRZnUEuxvD5KJpRq4sz6Bdx32LSsBA8kTcgUdLyBR0eJ2wZkVmPsDRGJ9ixb9vt3Y548TRKZl41lbSxMVSluAsai313Hl7A536.nRW80FrNIYmTdSVlWmsB.PHQQD.JlkzB9LyH5bSoB4nTaniRaaN0pFn07Q7L.DVr1iebBOPg; "
        "bh=%7B%22path%22%3A%22book%22%2C%22bid%22%3A%227630%22%2C%22bname%22%3A%22%E6%96%97%E7%BD%97%E5%A4%A7%E9%99%86V%E9%87%8D%E7%94%9F%E5%94%90%E4%B8%89%22%2C%22sid%22%3A%225336561%22%2C%22sname%22%3A%22%E5%BC%95%E5%AD%90%22%7D%2C%7B%22path%22%3A%22book%22%2C%22bid%22%3A%2210195%22%2C%22bname%22%3A%22%E5%89%91%E6%9D%A5%22%2C%22sid%22%3A%227144725%22%2C%22sname%22%3A%22%E7%AC%AC%E4%B8%80%E5%8D%B7%20%E7%AC%BC%E4%B8%AD%E9%9B%80%20%E7%AC%AC%E4%B8%80%E7%AB%A0%20%E6%83%8A%E8%9B%B0%22%7D; "
        "PHPSESSID=bo658utqcrh0jagjr5p7aj6o75; "
        "_ga_333KCL0K1B=GS2.1.s1792475468$o3$g1$t1792479821$j60$l0$h0"
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36",
    }

    @staticmethod
    def parse_cookie(cookie_str: str) -> dict:
        """将浏览器复制的 Cookie 字符串转为字典"""
        cookies = {}
        for item in cookie_str.split(";"):
            item = item.strip()
            if "=" in item:
                k, v = item.split("=", 1)
                cookies[k.strip()] = v.strip()
        return cookies

    def load_done_rows(self, existing: dict[int, dict] | None = None) -> dict[int, dict]:
        """读取已存在的 data.csv，合并已有记录，去重并按 index 排序写回"""
        done = dict(existing) if existing else {}
        if os.path.exists(self.csv_path):
            try:
                with open(self.csv_path, encoding="utf-8-sig", newline="") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        idx_str = (row.get("index") or "").strip()
                        content = (row.get("content") or "").strip()
                        if idx_str.isdigit() and content:
                            done[int(idx_str)] = {
                                "index": int(idx_str),
                                "volume": row.get("volume", ""),
                                "chapter": row.get("chapter", ""),
                                "content": content,
                            }
            except Exception as e:
                self.logger.warning(f"读取 {self.csv_path} 失败: {e}")

        if done:
            try:
                with open(self.csv_path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=["index", "volume", "chapter", "content"])
                    writer.writeheader()
                    for idx in sorted(done):
                        writer.writerow(done[idx])
            except Exception as e:
                self.logger.warning(f"写入 {self.csv_path} 失败: {e}")
        return done

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.done_rows = self.load_done_rows()
        self.done_indices = set(self.done_rows.keys())
        if self.done_indices:
            print(f"检测到已抓取 {len(self.done_indices)} 章，将自动跳过并继续续爬...", flush=True)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.on_engine_stopped, signal=scrapy.signals.engine_stopped)
        return spider

    def on_engine_stopped(self):
        """引擎完全停止、文件写入关闭后，自动合并历史数据、去重并按 index 排序"""
        self.load_done_rows(self.done_rows)

    async def start(self):
        cookie_dict = self.parse_cookie(self.raw_cookie)
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                headers=self.headers,
                cookies=cookie_dict,
                callback=self.parse,
                dont_filter=True,
            )

    def parse(self, response):
        # 遍历 dl#dir 下的 dt（卷名）和 dd（章节），将卷名与章节名分开存储
        chapters = []
        current_volume = ""
        for node in response.xpath('//dl[@id="dir"]/*'):
            tag = node.root.tag.lower()
            if tag == "dt":
                current_volume = node.xpath("normalize-space(string(.))").get(default="")
            elif tag == "dd":
                a = node.css("a")
                if a:
                    chapter_title = a.css("::text").get(default="").strip()
                    chapter_url = response.urljoin(a.attrib.get("href", ""))
                    chapters.append((current_volume, chapter_title, chapter_url))

        total = len(chapters)
        remaining = total - len(self.done_indices)
        print(f"共 {total} 章，已爬 {len(self.done_indices)} 章，剩余 {remaining} 章待抓取", flush=True)

        for index, (volume_title, chapter_title, chapter_url) in enumerate(chapters):
            if index in self.done_indices:
                continue
            yield scrapy.Request(
                url=chapter_url,
                headers=self.headers,
                callback=self.parse_chapter,
                priority=-index,
                cb_kwargs={
                    "index": index,
                    "volume_title": volume_title,
                    "chapter_title": chapter_title,
                    "chapter_url": chapter_url,
                },
            )

    def parse_chapter(self, response, index, volume_title, chapter_title, chapter_url):
        # 提取正文段落（排除 mask / chapter 占位节点，只取每个段落 div 的直接文本以去除水印标签）
        paragraphs = [
            "".join(div.xpath("./text() | ./span/text()").getall()).strip()
            for div in response.css("div#content > div:not(.mask):not(.chapter)")
        ]

        # 兼容页面直接内嵌 meta[name="client"] 的模式
        meta_token = response.css('meta[name="client"]::attr(content)').get()
        if meta_token:
            paragraphs = self.reorder_paragraphs(paragraphs, meta_token)
            yield {
                "index": index,
                "volume": volume_title,
                "chapter": chapter_title,
                "content": "\n".join(paragraphs),
            }
            print(f"[{index}] {volume_title} {chapter_title}", flush=True)
            return

        # 从章节 URL 中提取章节 ID（如 7144725.html -> r7144725.json）以获取段落排序 token
        sid_match = re.search(r"/(\d+)\.html", chapter_url)
        if sid_match:
            token_url = response.urljoin(f"r{sid_match.group(1)}.json?_=1")
            headers = {
                **self.headers,
                "Referer": chapter_url,
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest",
            }
            yield scrapy.Request(
                url=token_url,
                headers=headers,
                callback=self.parse_token,
                priority=10,
                cb_kwargs={
                    "index": index,
                    "volume_title": volume_title,
                    "chapter_title": chapter_title,
                    "paragraphs": paragraphs,
                },
            )

    @staticmethod
    def reorder_paragraphs(paragraphs: list[str], token: str) -> list[str]:
        """根据响应头中的 base64 token 还原被和图书打乱的段落顺序"""
        decoded = base64.b64decode(token).decode("utf-8")
        indices = [int(x) for x in re.split(r"[A-Z]+%", decoded) if x]
        ordered = [""] * len(paragraphs)
        b = 0
        for i, idx in enumerate(indices):
            if i >= len(paragraphs):
                break
            if idx < 5:
                ordered[idx] = paragraphs[i]
                b += 1
            else:
                ordered[idx - b] = paragraphs[i]
        return [p for p in ordered if p]

    def parse_token(self, response, index, volume_title, chapter_title, paragraphs):
        token = response.headers.get("token", b"").decode("utf-8")
        if token:
            paragraphs = self.reorder_paragraphs(paragraphs, token)
        content = "\n".join(paragraphs)

        yield {
            "index": index,
            "volume": volume_title,
            "chapter": chapter_title,
            "content": content,
        }
        print(f"[{index}] {volume_title} {chapter_title}", flush=True)
