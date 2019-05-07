# Facebook Parser/Grapher
### Parse all of your facebook messages using _**Python3**_  
Updated May 7th, 2019.

## Example Graphs 
<span><img src="https://user-images.githubusercontent.com/25948390/44682733-81fade80-aa44-11e8-8339-3a38a5d22f21.png" width="375">
<img src="https://user-images.githubusercontent.com/25948390/44682734-832c0b80-aa44-11e8-9d80-c9db0602de04.png" width="475">
</span>
<img src="https://user-images.githubusercontent.com/25948390/44682735-83c4a200-aa44-11e8-9ba5-9058bfaf2d56.png" width="425">
<img src="https://user-images.githubusercontent.com/25948390/44682739-84f5cf00-aa44-11e8-8b5d-1007614d8b2b.png" width="425">


## Setup
1. Clone this repository
2. Go to your [Facebook settings](https://www.facebook.com/settings) and select "Download a copy of your Facebook data" (should be under General Account Settings)  
  a. Login to Facebook  
  b. Click the down arrow beside the question mark button  
  c. Click "Settings"  
  d. From the left sidebar click "Your Facebook Information"  
  e. Click "Download Your Information"(all data, high quality)  
  f. Make sure the formatting is "JSON"   
  g. Download all of your Facebook data  
  
3. Place the unzipped download of your Facebook data into the same folder as this repository.  
4. Rename the unzipped folder to "facebook"  

## Usage
Remember, Python3 only.  
1. Install requirements  
      `pip install -r requirements.txt`  
2. update userinfo.py with your correct information  
3. run the correct parser for the formatting you chose  
      `python json_parse.py`
4. If you have Jupyter open analyze.ipynb    
  a. Run all the individual cells (This can easily be done by clicking "Cell" --> "Run All")  
  b. Graphs are somewhat interactive - you can zoom in and stuff  
  c. __skip step 5__
5. run analyze.py  
      `python analyze.py`  
6. Graphs will be saved in the 'graphs' folder
7. If you want to create a chatbot from your messages   
  a. run chatbot_export.py  
      `python chatbot_export.py`  
  b. go to the [facebook-messages-chatbot](https://github.com/ArmaanSethi/facebook-messages-chatbot) repo  
     
## Contributing
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## Additional Features Being Worked On
1. Creating a chat bot from your own facebook data. <br>
    - I have created a way to export the messages so you can train it using: <br>
  https://github.com/ArmaanSethi/facebook-messages-chatbot
  
2. Creating a way to measure average reply time <br>
    - I have no idea how I would create this metric, all help is welcome.
