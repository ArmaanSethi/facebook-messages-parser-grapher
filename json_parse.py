import os
import sqlite3
import json
from datetime import datetime, timedelta
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

def parse_file(f):
    with open(f) as json_file:
        data = json.load(json_file)

        if('title' not in data):#No title, seems to be when someone deletes their account
            title = data['thread_path']
        else:
            title = data['title']

        id = data['thread_path']

        group = True
        if( 'participants' not in data):#Talking to a bot
            group = True #I geuss treat as group chat
        else:
            if(len(data['participants']) == 1):
                group = False

        people_count = {}
        date_times = []
        texts = []
        images = []
        user = []

        for msg in data['messages']:
            # print(msg)
            if(not 'sender_name' in msg): #User Left Group or User Deleted Account
                usr = "NO SENDER NAME"
            else:
                usr = msg['sender_name']

            if usr in people_count:
                people_count[usr] += 1
            else: #Add person to people_count
                people_count[usr] = 1

            if(not 'content' in msg): #no text
                texts.append("")
                # print(msg)
            else:
                texts.append(msg['content'])

            if(not 'photos' in msg):#no photo url...there still can be sticker url
                images.append("")
            else:
                images.append(msg['photos'])


            date_times.append(datetime.fromtimestamp(int(msg['timestamp'])))
            user.append(usr)

    # print(date_times)
    print(id, title, people_count, len(date_times), len(texts), len(user), group)
    return(id ,str(title), people_count, date_times, texts, user, group)


root = "facebook/messages"
os.chdir(root)
files = os.listdir()

print("START")
fails = []
success = []
#ID, people{name:numMessages}, [dates, times, users, images]

for f in tqdm(files):
    try:
    # if(f != ".DS_Store" and f != "stickers_used"): #only times I ran into errors
        filename = os.path.join(f, "message.json")
        # print(f)
        success.append(parse_file(filename))
    except Exception:
        fails.append(f)
    print('\n')

pkl.dump(success, open("../../messages.pkl", "wb"))
pkl.dump(fails, open("../../fails.pkl", "wb"))
