import os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from tqdm import tqdm



def process(file):
    '''
    do your file processing here
    '''
    print("...started")
    soup = BeautifulSoup(open("facebook/messages/563.html", encoding='utf8').read(), 'html.parser')
    # soup = BeautifulSoup(open("facebook/messages/635.html", encoding='utf8').read(), 'html.parser')
    print("Opened messages.htm")
    soup = soup.find_all("div", class_="message")

    group = []
    time = []
    date = []
    message = []
    user = []

    for msg in tqdm(soup):
        date.append(msg.find_all("span", class_="meta")[0].contents[0])
        user.append(msg.find_all("span", class_="user")[0].contents[0])
        try:
            text = msg.find_next_sibling("p").contents[0]
        except:
            text = ""
        message.append(text)


    """OUTPUT"""
    print(len(date))
    print(len(user))
    print(len(message))

    size = len(date)
    for i in range(size):
        print(user[size-1-i], '\t', message[size-1-i],'\t', date[size-1-i])
    return 0

def recursion(path):
    output = []
    for file in os.listdir(path):
        if os.path.isdir(file):
            output += recursion(file)
        else:
            output.append(process(file))

    return output

process('')