rm data.csv
scrapy crawl ranwen --nolog -o data.csv
python3 txt-converter.py
mv sorted-data.csv ../Novel-Reader/data.csv
