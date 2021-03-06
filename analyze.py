import os
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from tqdm import tqdm
import pickle as pkl
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

from userinfo import YOUR_NAME, START_DAY, END_DAY

"""GOALS"""
# Cumulative Messaging per person
# Number of people messaged per day
# Total Sent/Received
"""--------------------------------------------------------------------"""

print(YOUR_NAME, START_DAY, END_DAY)
Num_People_To_Graph = 10
# START_DAY = "8/20/16"
# END_DAY = "6/1/18"

if(not os.path.exists("graphs")):
    os.mkdir("graphs")
"""--------------------------------------------------------------------"""

convos = pkl.load(open("messages.pkl", 'rb'))
#0: id (string)
#1: name (string)
#2: num_messages (dict name:num_messages)
#3: datetime (list of datetime objs)
#4: text (list of messages)
#5: who (list of names)
#6: group (bool)
print("Total Conversations: ", len(convos), "\n")

"""--------------------------------------------------------------------"""

start_day = datetime.strptime(START_DAY, "%m/%d/%y")
end_day = datetime.strptime(END_DAY, "%m/%d/%y")
num_days = (end_day - start_day).days
num_days

"""--------------------------------------------------------------------"""
df_mpd = pd.DataFrame()
df_mpd_me = pd.DataFrame()

date_list = [start_day.date() + timedelta(days=x) for x in range(0, num_days+1)]

for i in range(len(convos)):
    messages_per_day = []
    messages_per_day_me = []
    if(convos[i][6] == False):# not group chat
        num_messages = len(convos[i][3]) 
        
        total_messages = 0
        total_messages_me = 0
        prev_total_messages = 0
        prev_total_messages_me = 0
        for day in date_list:
            while(total_messages < num_messages and convos[i][3][num_messages - total_messages - 1].date() < day):
                total_messages+=1 #messages until day
                if(convos[i][5][num_messages - total_messages - 1] == YOUR_NAME):
                    total_messages_me += 1
                
            messages_per_day.append(total_messages - prev_total_messages) #num messages per day
            messages_per_day_me.append(total_messages_me - prev_total_messages_me) #num messages by me per day
            prev_total_messages = total_messages #update total
            prev_total_messages_me = total_messages_me #update total
        if(sum(messages_per_day[1:]) > 0): #no need to add columns with no messages
            df_mpd[convos[i][1]] = messages_per_day[1:]
            df_mpd_me[convos[i][1]] = messages_per_day_me[1:]

df_mpd.index = date_list[:-1]
df_mpd_me.index = date_list[:-1]

df_mpd = df_mpd.reindex(sorted(df_mpd.columns), axis=1) #sort alphabetically, later sort by total messages
df_mpd_me = df_mpd_me.reindex(sorted(df_mpd_me.columns), axis = 1)


"""--------------------------------------------------------------------"""
df_mpd.head()#messages per day
df_mpd_me.head()# messages by me per day

"""--------------------------------------------------------------------"""
#sort by total num messages
df_mpd = df_mpd[df_mpd.sum().sort_values(ascending = False).index]
df_mpd.head()
"""--------------------------------------------------------------------"""
#messages per person per day
df_mpp_pd = df_mpd.copy().cumsum(axis=0)
df_mpp_pd = df_mpp_pd.iloc[:,:Num_People_To_Graph]
df_mpp_pd.head()
"""--------------------------------------------------------------------"""
plt_mpp_pd = df_mpp_pd.plot(title = "Cumulative Messages Per Person Per Day", figsize=(12,12))
plt_mpp_pd.set_ylabel("Total Messages")
plt_mpp_pd.set_xlabel("Date")
plt_mpp_pd.grid(True, linestyle='--')
plt_mpp_pd.axhline(y=0, color='k')

plt_mpp_pd.get_figure().savefig("graphs/cumulative_messaging_by_day.png", bbox_inches='tight')
"""--------------------------------------------------------------------"""
#total messages per day
df_tm_pd = df_mpd.iloc[:].sum(axis = 1)
df_tm_pd.head()
"""--------------------------------------------------------------------"""
import matplotlib.dates as mdates

plt_tm_pd = plt.figure()

plt_tm_pd = df_tm_pd.plot(title = "Total Messages Per Day", figsize=(12,5))
plt_tm_pd.set_ylabel("Total Messages")
plt_tm_pd.set_xlabel("Date")
plt_tm_pd.grid(True, linestyle='--')
plt_tm_pd.axhline(y=0, color='k')
plt_tm_pd.axhline(y=np.mean(df_tm_pd), color='g', linestyle='--')

plt_tm_pd.get_figure().savefig("graphs/total_messages_per_day.png", bbox_inches='tight')
"""--------------------------------------------------------------------"""
#num people messaged per day
df_ppl_pd = (df_mpd != 0).astype(int).sum(axis = 1)
df_ppl_pd.head()
"""--------------------------------------------------------------------"""
plt_ppl_pd = plt.figure()
plt_ppl_pd = df_ppl_pd.plot(title = "Number of People Talked to", figsize=(12,5))
plt_ppl_pd.set_ylabel("Number of People")
plt_ppl_pd.set_xlabel("Date")
plt_ppl_pd.grid(True, linestyle='--')
plt_ppl_pd.axhline(y=0, color='k')
plt_ppl_pd.axhline(y=np.mean(df_ppl_pd), color='g', linestyle = '--')

plt_ppl_pd.get_figure().savefig("graphs/num_people_talked_per_day.png", bbox_inches='tight')
"""--------------------------------------------------------------------"""
df_mpd = df_mpd.reindex(sorted(df_mpd.columns), axis=1)#sort alphabetically again
df_mpd.head()
"""--------------------------------------------------------------------"""
df_total_me = pd.DataFrame()

df_total_me['sent'] = df_mpd_me.sum()
df_total_me['received'] = df_mpd.sum() - df_total_me['sent']

df_total_me = df_total_me.reindex(df_total_me.sum(axis = 1).sort_values(ascending = False).index)
df_total_me[:Num_People_To_Graph]
"""--------------------------------------------------------------------"""
plt_total_me = df_total_me[:Num_People_To_Graph+5].plot.bar(title="Total Messages Sent/Received (Top "+ str(Num_People_To_Graph+5) + " Most Talked To)", stacked=True, figsize=(12, 8))
plt_total_me.set_ylabel("Number of Messages")
plt_total_me.set_xlabel("Person")
plt.tight_layout()

plt_total_me.get_figure().savefig("graphs/total_sent_received.png", bbox_inches='tight')
"""--------------------------------------------------------------------"""
#Made by your boy Armaan, if you got any cool ideas hit him up...or Fork/Pull Request --> you know the deal