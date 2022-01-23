# Novel Spider

## 稻草人书屋

* 网页：https://www.20dcr.com/
* 从某一章开始爬取

```shell
scrapy crawl daocaoren --nolog -o data.csv
```

* 生成txt

```sh
python txt-converter.py
```

## 燃文网

* 网页：https://www.ranwen.la/
* 从某一章开始爬取

```shell
scrapy crawl ranwen --nolog -o data.csv
```

* 生成txt

```sh
python txt-converter.py
```
## 飘香文学

* 网页：https://www.ptwxz.com/

```shell
scrapy crawl piaoxiang --nolog -o data.csv
```

* 生成txt

```sh
python txt-converter.py
```
