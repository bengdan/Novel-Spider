import pandas as pd

data = pd.read_csv("./data.csv")

txt = ""
for index, row in data.iterrows():
    txt += row["chapter"] + "\n"
    txt += row["content"] + "\n"
with open("novel.txt", 'w',encoding="utf-8") as f:
    f.write(txt)
