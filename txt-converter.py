import pandas as pd

data = pd.read_csv("./data.csv")

txt = ""
for index, row in data.iterrows():
    txt += str(row["chapter"]) + "\n"
    txt += str(row["content"]) + "\n"
with open("novel.txt", 'w',encoding="utf-8") as f:
    f.write(txt)
