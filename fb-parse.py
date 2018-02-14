import os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from tqdm import tqdm



def parse_file(f):
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

def find_html_filenames( path_to_dir, suffix=".html" ):
    filenames = os.listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]

def parse_folder():
    os.chdir("facebook/messages")
    print(os.getcwd())
    files = find_html_filenames(os.getcwd())

    for f in tqdm(files):
        parse_file(f)
        print()


parse_folder()
# parse_file("facebook/messages/356.html") #has no user but has names
# parse_file("facebook/messages/421.html") #has no name but has messages
# parse_file("facebook/messages/7.html") #group chat
