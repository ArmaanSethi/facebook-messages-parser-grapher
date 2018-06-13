import os
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date, time
from tqdm import tqdm
import pickle as pkl
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

from userinfo import YOUR_NAME, START_DAY, END_DAY

#Things I ignore
#Reactions, ownloaded files, Audio files, Plans

#Things to do
#Db
#gender
def fb_to_datetime(date_time):
    months={"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
    
    dt = date_time.split(" ")
    date_str = " ".join(dt[0:-1])
    time_str = str(dt[-1])

    year=date_str[8:]
    month=months[date_str[0:3]]
    day=date_str[4:6]

    time_components=time_str.split(":")
    hour=int(time_components[0])
    if(hour == 12):
        hour = 0
    if(time_components[1][-2] == 'p'):
        hour+=12
    minute=time_components[1][:2]
    second=0

    d = date(int(year), int(month), int(day))
    t = time(int(hour), int(minute), int(second))
    dt = datetime.combine(d,t)

    return dt

def parse_file(f):
    print(f, "Opening HTML File(this may take a while)")
    soup = BeautifulSoup(open(f, encoding='utf8').read(), 'html.parser')

    title = soup.find("title").contents[0]
    main = soup.find("div", {"role": "main"})
    children = main.findChildren(recursive = False)

    gc = children[0].find("div", {"class": "_2lek"})
    #print(gc.contents[0])
    people = [] #dictonary of person:num messages
    group = False
    if (gc.contents[0][0:14] == "Participants: "):
        #Group Chat
        group = True
        people.append(gc.contents[0]) 
        #PARSE FOR LIST OF NAMES LATER
    else:
        #Not Group Chat
        people.append(soup.find("title").contents[0])

    # print("People: ", people)

    people_count = {}
    date_times = []
    texts = []
    images = []
    user = []

    for msg in enumerate(children):
        i = msg[0]
        if(group and i == 0):
            continue

        try:
            date_time = children[i].find_all("div", class_ = "_2lem")[0].contents[0]
        except Exception:
            print("DATE FAIL", children[i])
            continue

        usr = str(children[i].find_all("div", class_= "_2lel")[0].contents[0])
        if usr in people_count:
            people_count[usr] += 1
        else:
            people_count[usr] = 1
        # print("usr: ", usr)

        things = children[i].find_all("div", class_= "_2let")[0].contents[0].find_all("div")
        text = ""
        img = ""
        try:
            text = things[1].contents[0]
        except Exception:
            text = ""
        try:
            img = things[4].find_all("img")[0]['src']
        except Exception:
            img = ""

        # if text == img == "":
        #     print("NO TEXT, NO IMAGE: ", i)
        #     print(things)
        #     input()

        # print( fb_to_datetime(date_time) )
        

        date_times.append(fb_to_datetime(date_time))
        texts.append(str(text))
        images.append(str(img))
        user.append(str(usr))

    print(people_count)
    print(len(texts), texts[-1])
    print(len(user), user[-1])
    return(f[:-13],str(title), people_count, date_times, texts, user, group)

root = "facebook/messages"
os.chdir(root)
files = os.listdir()

print("START")
fails = []
success = []
#ID, people{name:numMessages}, [dates, times, users, images]
for f in tqdm(files):
    try:
        filename = os.path.join(f, "message.html")
        success.append(parse_file(filename))
    except Exception:
        print("Failed to parse", root+"/"+filename)
        fails.append(f)
    print('\n')

pkl.dump(success, open("../../messages.pkl", "wb"))
pkl.dump(fails, open("../../fails.pkl", "wb"))
