import os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from tqdm import tqdm

"""Fields we care about"""
#Title
#People
#Times
#Dates
#Messages
#User

def parse_file(f):
    print(f, "Opening HTML File(this may take a while)")
    soup = BeautifulSoup(open(f, encoding='utf8').read(), 'html.parser')
    try:
        people = soup.find("h3").next_sibling.split(":")[1].split(',') #people in conversation
    except:
        print("No people?")
        return #there are no people ???? (happens when someone deletes their account maybe?)
    
    # print("Ppl", people)

    title = soup.find("title").contents[0][18:] #name of conversation
    # print("TITLE", title)

    # print("Opened messages.htm")
    soup = soup.find_all("div", class_="message")

    group = False
    if len(people) > 1:
        group = True

    times = []
    dates = []
    texts = []
    user = []

    for msg in tqdm(soup):
        (date, time) = msg.find_all("span", class_="meta")[0].contents[0].split(" at ")
        try:
            usr = msg.find_all("span", class_="user")[0].contents[0]
            # user.append(msg.find_all("span", class_="user")[0].contents[0])
        except:
            if(not group):
                usr = people[0][1:]
            else:
                usr = ""
        try:
            text = msg.find_next_sibling("p").contents[0]
        except:
            text = ""

        dates.append(date)
        times.append(time)
        texts.append(text)
        user.append(usr)


    """OUTPUT"""
    # print(len(dates))
    # print(len(user))
    # print(len(texts))
    num_messages = len(dates) #number of messages
    """Output all messages in order"""
    # for i in range(num_messages):
    #     print(user[num_messages-1-i], '\t', texts[num_messages-1-i],'\t', dates[num_messages-1-i])


def find_html_filenames( path_to_dir, suffix=".html" ):
    filenames = os.listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]


def parse_folder():
    os.chdir("facebook/messages")
    print(os.getcwd())
    files = find_html_filenames(os.getcwd())

    for f in tqdm(files):
        parse_file(f)


# parse_folder()
# parse_file("facebook/messages/356.html") #has no user but has names
# parse_file("facebook/messages/421.html") #has no name but has messages
parse_file("facebook/messages/7.html") #group chat
