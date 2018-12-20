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

# Things that are ignored
# Reactions, downloaded files, Audio files, Plans

def parse_file(f):
    with open(f) as json_file:
        data = json.load(json_file)

        if('title' not in data): # No title, seems to be when someone deletes their account
            title = data['thread_path']
        else:
            title = data['title']

        id = data['thread_path']

        group = True
        if( 'participants' not in data): # Talking to a bot
            group = True # I guess treat as group chat
        else:
            if(len(data['participants']) <= 2):
                group = False

        people_count = {}
        date_times = []
        texts = []
        images = []
        user = []

        for msg in data['messages']:
            if(not 'sender_name' in msg): # User left the group or User Deleted Account
                usr = "NO SENDER NAME"
            else:
                usr = msg['sender_name']

            if usr in people_count:
                people_count[usr] += 1
            else: #Add person to people_count
                people_count[usr] = 1

            if(not 'content' in msg): #no text
                texts.append("")
            else:
                texts.append(msg['content'])

            if(not 'photos' in msg): #no photo url...there still can be sticker url
                images.append("")
            else:
                images.append(msg['photos'])

            if(not 'timestamp_ms' in msg):
                timestamp = int(msg['timestamp'])
            else:
                timestamp = int(int(msg['timestamp_ms'])/1000)

            date_times.append(datetime.fromtimestamp(timestamp))
            user.append(usr)

    return(id ,str(title), people_count, date_times, texts, user, group)

def list_files(paths):
    files = []
    root = os.getcwd()
#     print(root)
    for path in paths:
#         print(os.getcwd())
        os.chdir(path)
        prefix = os.getcwd()
        f = os.listdir()
        files.extend(list(map(lambda x: prefix+"/"+x, f)))
        os.chdir(root)
        
    return files

paths = ["facebook/messages/archived_threads", "facebook/messages/inbox"]
files = list_files(paths)
# print("START")
fails = []
success = []

for f in tqdm(files):
    try:
        if(f != ".DS_Store"): # ignore other generic files
            filename = os.path.join(f, "message.json")
            success.append(parse_file(filename))
    except Exception as e:
        print("Failed to parse. Exception: ", repr(e), " ", root, "/", filename)
        fails.append(f)

pkl.dump(success, open("messages.pkl", "wb"))
pkl.dump(fails, open("fails.pkl", "wb"))