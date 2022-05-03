from urllib import response
import tweepy
import json
import requests
import logging

from Wallpaper import *
from credentials import *


from datetime import datetime

today = datetime.today().strftime('%Y-%m-%d')
day = int(datetime.today().strftime('%d'))
month = int(datetime.today().strftime('%m'))
year = int(datetime.today().strftime('%Y'))

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# For adding logs in application
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)

def zeller(date, month, year):   # Day, Month, Year in full
    if (month < 3):
        # January and February are months 13 and 14 of the previous year
        month += 12
        year -= 1;
        
    # separate out the century and year parts
    j = int(year / 100)
    k = int(year % 100)
    
    # calculate the day of the week
    dow = int((date + ((13 * (month + 1)) / 5) + k + int(k / 4) + int(j / 4) + (5 * j)) % 7)

    if dow == 1:
        day = "Sunday"
    elif dow == 2:
        day = "Monday"
    elif dow == 3:
        day = "Tuesday"
    elif dow == 4:
        day = "Wednesday"
    elif dow == 5:
        day = "Thursday"
    elif dow == 6:
        day = "Friday"
    else:
        day = "Saturday"

    return day
dayname = zeller(day,month,year)
print('Today is', dayname)
import requests, shutil, json
url = 'https://meme-api.herokuapp.com/gimme'
data = {"postLink":"","url":""}
response = requests.get(url, data=data)
print(response.text)
j = json.loads(response.text)
image_url = j['url']
reddit = j['postLink']
resp = requests.get(image_url, stream=True)
local_file = open('created_image.jpg', 'wb')
resp.raw.decode_content = True
shutil.copyfileobj(resp.raw, local_file)
del resp

def get_quote():
    url = "https://api.quotable.io/random"

    try:
        response = requests.get(url)
    except:
        logger.info("Error while calling API...")
    res = json.loads(response.text)
    print(res)
    return res['content'] + "-" + res['author']

def get_last_tweet(file):
    f = open(file, 'r')
    lastId = int(f.read().strip())
    f.close()
    return lastId

def put_last_tweet(file, Id):
    f = open(file, 'w')
    f.write(str(Id))
    f.close()
    logger.info("Updated the file with the latest tweet Id")
    return


def respondToTweet(file='tweet_ID.txt'):
    last_id = get_last_tweet(file)
    mentions = api.mentions_timeline(last_id, tweet_mode='extended')
    if len(mentions) == 0:
        return

    new_id = 0
    logger.info("someone mentioned me...")

    for mention in reversed(mentions):
        logger.info(str(mention.id) + '-' + mention.full_text)
        new_id = mention.id

        if '#quote' in mention.full_text.lower():
            logger.info("Responding back with QOD to -{}".format(mention.id))
            try:
                tweet = get_quote()
                get_wallpaper(tweet)

                media = api.media_upload("created_image.png")

                logger.info("liking and replying to tweet")

                api.create_favorite(mention.id)
                api.update_status('@' + mention.user.screen_name + " Here's your Quote", mention.id,
                                  media_ids=[media.media_id])
            except:
                logger.info("Already replied to {}".format(mention.id))
        
        if '#meme' in mention.full_text.lower():
            print('Tweeting...')
#api.update_with_media("/home/pi/todaymemebot/local_image.jpg", status = 'Today is a {0}\nHere\'s A Random Meme from {1}'.format(dayname, reddit))
            media = api.media_upload("created_image.jpg")
            api.update_status('@' + mention.user.screen_name +' Today is a {0}\nHere\'s A Random Meme from {1}'.format(dayname, reddit), media_ids=[media.media_id])
            print('done')

         
        


    put_last_tweet(file, new_id)

if __name__=="__main__":
    respondToTweet()