import os
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from tqdm import tqdm

#Things I ignore
#Reactions, ownloaded files, Audio files, Plans

#Things to do
#Fix People
#Db

def parse_file(f):
    print(f, "Opening HTML File(this may take a while)")
    soup = BeautifulSoup(open(f, encoding='utf8').read(), 'html.parser')

    main = soup.find("div", {"role": "main"})
    children = main.findChildren(recursive = False)


    gc = children[0].find("div", {"class": "_2lek"})
    #print(gc.contents[0])
    people = []
    group = False
    if (gc.contents[0][0:14] == "Participants: "):
        #Group Chat
        group = True
        people.append(gc.contents[0]) 
        #PARSE FOR LIST OF NAMES LATER
    else:
        #Not Group Chat
        people.append(soup.find("title").contents[0])

    print("People: ", people)


    times = []
    dates = []
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

        usr = children[i].find_all("div", class_= "_2lel")[0].contents[0]
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

        if text == img == "":
            print("NO TEXT, NO IMAGE: ", i)
            print(things)
            # input()


        dt = date_time.split(" ")
        dates.append(" ".join(dt[0:-1]))
        times.append(dt[-1])
        texts.append(text)
        images.append(img)
        user.append(usr)

    # print(len(dates), dates[-1])
    # print(len(times), times[-1])
    # print(len(texts), texts[-1])
    # print(len(user), user[-1])

        


print("\n\n\n\n\n")
root = "facebook/messages"
os.chdir(root)
files = os.listdir()

print("START")
for f in tqdm(files):
    if(not f.startswith('.')):
        print('\n\n\n\n')
        filename = os.path.join(f, "message.html")
        parse_file(filename)
