"""
The prototype for a manhwa webscraper

The purpose is to notify the user when a manhwa that they follow reaches a
certain amount of new chapters.

Has support for Line Webtoon, Reaper Scans, Asura Scans and Flame Scans

Author:Jason X
"""

import os
from utils import *

# load and update manga database
dl = r"C:\Users\Francis Xavier\Documents\Python\timebomb\database.py"

db = MangaDatabase();
db.load(dl)
db.update()
db.save(dl)

# show manga with 20+ unread chapters
db.unread(20).show(1)
os.system("pause")
"""
RANDOM CODE THAT WAS MADE DURING TESTING:

pickle helper

LOAD:
variable = pickle.load(open("file_name.p", "rb"))

SAVE:
pickle.dump(variable, open("file_name.p", "wb"))

#take data from spreadsheet and add it to the database
workbook = load_workbook('Timebomb.xlsx', read_only=True)
sheet = workbook.active

for item in sheet["A22:E26"]:
    db.add(ReaperScans(item[0].value, item[1].value, item[2].value, item[3].value))

for item in sheet["A27:E40"]:
    db.add(ReaperScans(item[0].value, item[1].value, item[2].value, item[3].value))

#FlameScans requires same processing as Asura
for item in sheet["A14:E15"]:
    db.add(ReaperScans(item[0].value, item[1].value, item[2].value, item[3].value))

for item in sheet["A41:E45"]:
    db.add(ReaperScans(item[0].value, item[1].value, item[2].value, item[3].value))

for item in sheet["A16:E21"]:
    db.add(MangaPlus(item[0].value, item[1].value, item[2].value, item[3].value))

db.update_all()
db.save()

#defunct test case
test = LineWebtoon('Omniscient Reader', datetime.datetime.today(), 'https://www.webtoons.com/en/action/omniscient-reader/list?title_no=2154', 61)
test.update()
"""