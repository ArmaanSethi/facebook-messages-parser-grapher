from tqdm import tqdm
import pickle as pkl

from userinfo import YOUR_NAME, START_DAY, END_DAY

"""--------------------------------------------------------------------"""

# from A to B
# from B to A
# from A to B
# from B to A
# from A to B
# ===
# from C to D
# from D to C
# from C to D
# ===
# from E to F
# from F to E
# from E to F
# from F to E

#format for chatbot txt

"""--------------------------------------------------------------------"""

convos = pkl.load(open("messages.pkl", 'rb'))
#1: name (string)
#2: num_messages (dict name:num_messages)
#3: datetime (list of datetime objs)
#4: text (list of messages)
#5: who (list of names)
#6: group (bool)
file = open("chatbot.txt","w") 
 
print("Total Conversations: ", len(convos), "\n")

"""--------------------------------------------------------------------"""

for convo in tqdm(convos):
    for msg in reversed(convo[4]):
        if(msg != '===' or msg != ""):
            file.write(msg + '\n')
    file.write("===")
    
file.close()