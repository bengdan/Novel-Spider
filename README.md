# Novel Spider

## 稻草人书屋

* 网页：https://www.20dcr.com/
* 从某一章开始爬取

```shell
scrapy crawl daocaoren --nolog -o data.csv
```

* 生成txt

```sh
python3 txt-converter.py
```

## 燃文网

* 网页：https://www.ranwen.la/
* 从某一章开始爬取

```shell
scrapy crawl ranwen --nolog -o data.csv
```

* 生成txt

```sh
python3 txt-converter.py
```
## 飘香文学

* 网页：https://www.ptwxz.com/

```shell
scrapy crawl piaoxiang --nolog -o data.csv
```

* 生成txt

```sh
python3 txt-converter.py
```
## 努努书坊

* 网页：https://www.kanunu8.com/

```shell
scrapy crawl nunu --nolog -o data.csv
```

* 生成txt

```sh
python3 txt-converter.py
```

## 爱看小说

* 网页：https://m.bqg121.com/

```shell
scrapy crawl aikan --nolog -o data.csv
```

* 生成txt

```sh
python3 txt-converter.py
```
