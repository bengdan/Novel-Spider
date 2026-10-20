# Novel Spider

用 Scrapy 按章节爬小说，导出 CSV，再转成 EPUB。

## 环境

依赖用 Pipenv 管理，需要 Python 3.13：

```shell
pipenv install
pipenv shell
```

下面的命令都在 `pipenv shell` 里执行。

## 使用

1. 打开 `novel/spiders/` 里对应站点的爬虫，把 `start_urls` 改成要爬的书的目录页。
2. 爬取，结果写到 `data.csv`：

   ```shell
   scrapy crawl ranwen --nolog -o data.csv
   ```

3. 按章节顺序排好，输出 `sorted-data.csv`，同时删掉 `data.csv`：

   ```shell
   python txt-converter.py
   ```

4. 转成 EPUB，书名默认取文件名：

   ```shell
   python epub-converter.py sorted-data.csv --title 书名 --author 作者
   ```

   `data.csv` 也可以跳过第 3 步直接转，脚本会按 `index` 列排序。支持通配符批量转换（`python epub-converter.py *.csv -o epub`）和 `--cover` 封面，完整参数见 `python epub-converter.py -h`。

`run.sh` 用 `ranwen` 跑完第 2、3 步，再把 `sorted-data.csv` 挪到 `../Novel-Reader/data.csv`。

## 支持的站点

| 爬虫 | 站点 | 说明 |
| --- | --- | --- |
| `aikan` | [爱看小说](https://m.bqg121.com/) | |
| `daocaoren` | [稻草人书屋](https://www.20dcr.com/) | 只爬作者和书目列表（书名、链接），不爬正文 |
| `fanqie` | [番茄小说](https://fanqienovel.com/) | 需要登录 cookie，正文有字体反爬，见下文 |
| `kuiba` | [九九藏书网](https://www.99csw.com/) | 还没写完 |
| `nunu` | [努努书坊](https://www.kanunu8.com/) | |
| `piaoxiang` | [飘香文学](https://www.piaotian.com/) | |
| `ranwen` | [燃文网](https://www.ranwen.la/) | 从目录第 16 条开始爬，起点在 `contents[15:]` 里调 |
| `sanshao` | [tj1024.com](https://www.tj1024.com/) | |
| `hetushu` | [和图书](https://www.hetushu.com/index.php) | 还没有对应的爬虫文件 |

## 番茄小说

番茄需要登录，cookie 写在 `novel/spiders/fanqie.py` 的 `cookie_raw` 里，过期了要换。

番茄正文里有一部分字被换成了私用区字符，页面靠自定义字体才显示成正常的字，所以直接爬下来是乱码。`fanqie.py` 里的 `recover_dict` 是这些码位到真实汉字的对照表，用 `tools/fanqie-font/` 里的工具生成：

- `fanqie.woff2`：从番茄页面下载的字体文件。
- `font-test.html`：用这个字体按码位顺序显示全部加密字符，在浏览器里打开，照着认字。
- `font-test.py`：把认出来的字（`actual_chars`）按顺序对到字体的码位上，生成同目录下的 `dict.json`，内容就是 `recover_dict`。

```shell
python tools/fanqie-font/font-test.py
```
