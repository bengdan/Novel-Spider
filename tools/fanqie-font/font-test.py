import os

from fontTools.ttLib import TTFont

# read and write next to this script, wherever it is run from
HERE = os.path.dirname(os.path.abspath(__file__))

font = TTFont(os.path.join(HERE, "fanqie.woff2"))

cmap = font['cmap']

cmap_dict = cmap.getBestCmap()

actual_chars = "D在主特家军然表场4要只v和6别还g现儿岁此象月3出战工相o男直失世F都平文什VO将真T那当会立些u是十张学气大爱两命全后东性通被1它乐接而感车山公了常以何可话先pi叫轻M士w着变尔快l个说少色里安花远7难师放t报认面道S克地度I好机U民写把万同水新没书电吃像斯5为y白几日教看但第加候作上拉住有法r事应位利你声身国问马女他Y比父xAHNSX边美对所金活回意到z从j知又内因点Q三定8Rb正或夫向德听更得告并本q过记L让打f人就者去原满体做经K走如孩cG给使物最笑部员等受k行一条果动光门头见往自解成处天能于名其发总母的死手入路进心来h时力多开已许d至由很界n小与Z想代么分生口再妈望次西风种带J实情才这E我神格长觉间年眼无不亲关结0友信下却重己老2音字m呢明之前高PB自太e9起稜她也W用方子英每理便四数期中C外样a海们任"

dict = {}

lyst = list()
for index, (unicode_val, glyph_name) in enumerate(cmap_dict.items()):
    unicode_hex = hex(unicode_val)
    # print(f"Index: {index}, Unicode: {unicode_val}")
    dict[unicode_val] = actual_chars[index]
    lyst.append(f"&#x{unicode_hex[2:]};")


# save to json file
import json

with open(os.path.join(HERE, "dict.json"), 'w',encoding="utf-8") as f:
    json.dump(dict, f, ensure_ascii=False, indent=4)

