import pandas as pd

data = pd.read_csv("./data.csv")

data = data.sort_values(by=['index'])

# save sorted data csv
data.loc[:, data.columns != 'index'].to_csv("./sorted-data.csv",index = False)

txt = ""
for index, row in data.iterrows():
    txt += str(row["chapter"]).split("（")[0] + "\n"
    txt += str(row["content"]) + "\n"

# save to txt
with open("novel.txt", 'w',encoding="utf-8") as f:
    f.write(txt)
