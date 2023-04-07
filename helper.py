import tweepy as tw
import pandas as pd
import re
from textblob import TextBlob
import streamlit as st
import datetime
import configparser
from src.logger import logging
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from src.exeption import CustomException
import sys


emoj = re.compile("["
        u"\U00002700-\U000027BF"  # Dingbats
        u"\U0001F600-\U0001F64F"  # Emoticons
        u"\U00002600-\U000026FF"  # Miscellaneous Symbols
        u"\U0001F300-\U0001F5FF"  # Miscellaneous Symbols And Pictographs
        u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        u"\U0001F680-\U0001F6FF"  # Transport and Map Symbols
        u"[\U00010000-\U0010ffff]"
                      "]+", re.UNICODE)


def twitter_connection():
    try:
        logging.info("twitter connection establishment")
        config=configparser.ConfigParser()
        config.read("config.ini")

        api_key=config["twitter"]["consumerKey"]
        api_key_secret = config["twitter"]["consumerSecret"]
        access_token = config["twitter"]["accessToken"]
        access_token_secret=config["twitter"]["accessTokenSecret"]
        auth = tw.OAuthHandler(api_key, api_key_secret)
        auth.set_access_token("access_token", "access_token_secret")
        api = tw.API(auth) 
        logging.info("API key return")
        return api
    except Exception as e:
        raise CustomException(e,sys)


api=twitter_connection()
logging.info("API key initiated")

def textclean(text):
    try:
        text = re.sub('@[A-Za-z0–9]+', '', text) #Removing @mentions
        text = re.sub('#', '', text) # Removing '#' hash tag
        text = re.sub('RT[\s]+', '', text) # Removing RT
        text = re.sub('https?:\/\/\S+', '', text)
        text = re.sub("\n","",text) # Removing hyperlink
        text = re.sub(":","",text) # Removing hyperlink
        text = re.sub("_","",text) # Removing hyperlink
        text = emoj.sub(r'', text)
        logging.info("text cleaning done")
        return text
    except Exception as e:
        raise CustomException(e,sys)

def mention_extract(text):
    text=re.findall(r"(@[A-Za-z0-9\d\w]+)",text)
    logging.info("mention extract")
    return text

def hashtag_extract(text):
    text=re.findall(r"(#[A-Za-z0-9\d\w]+)",text)
    logging.info("hashtag extract")
    return text

def Subjectivity(text):
    return TextBlob(text).sentiment.subjectivity

def getPolarity(text):
    return TextBlob(text).sentiment.polarity

def url_extract(text):
    text = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text)
    return text
def retweet_extract(text):
    text=re.findall(r'(RT[\s@[A-Za-z0–9\d\w]+)',text)
    return text

def sentiment(score):
    if score<0:
        return 'Negative'
    elif score==0:
        return 'Neutral'
    else:
        return 'Positive'
    
@st.cache(allow_output_mutation=True)
def preprocessing_data(query,tweet_number,option):
    try:
        if option == "hashtag":
            posts = tw.Cursor(api.search_tweets, q=query, count = 200, lang ="en", tweet_mode="extended").items((tweet_number))
    
        if option == "Name":
            posts = tw.Cursor(api.user_timeline, screen_name=query, count = 200, tweet_mode="extended").items((tweet_number))
    
        data  = pd.DataFrame([tweet.full_text for tweet in posts], columns=['Tweets'])
        data['mention']=data['Tweets'].apply(mention_extract)
        data['hashtag']=data['Tweets'].apply(hashtag_extract)
        data['Url']=data['Tweets'].apply(url_extract)
        data['retweet']=data['Tweets'].apply(retweet_extract)

        data['Tweet']=data['Tweets'].apply(textclean)
        data['Subjectivity'] = data['Tweets'].apply(Subjectivity)
        data['Polarity'] = data['Tweets'].apply(getPolarity)

        data['Analysis'] = data['Polarity'].apply(sentiment)
        logging.info('preprocessing and columns added')
        return data
    except Exception as e:
        raise CustomException(e,sys)


def download_data(data):
    try:
        logging.info('csv file downloaded')
        dataframe=st.download_button(
            label="Download data as csv",
            data=data.to_csv(),
            file_name="twitter_data.csv",
            mime='text/csv',
            help = "When You Click On Download Button You can download your CSV File"
        )
        return dataframe
    except Exception as e:
        raise CustomException(e,sys)

def mention_data(data):
    try:
        mention = pd.DataFrame(data["mentions"].to_list()).add_prefix("mention_")

        try:
            mention = pd.concat([mention["mention_0"], mention["mention_1"], mention["mention_2"]], ignore_index=True)
        except:
            mention = pd.concat([mention["mention_0"]], ignore_index=True)
    
        mention = mention.value_counts().head(10)
        logging.info('mention data function call and return of data')
    
        return mention
    except Exception as e:
        raise CustomException(e,sys)


def analyse_hastag(data):
    try:
        hastag = pd.DataFrame(data["hastags"].to_list()).add_prefix("hastag_")

        try:
            hastag = pd.concat([hastag["hastag_0"], hastag["hastag_1"], hastag["hastag_2"]], ignore_index=True)
        except:
            hastag = pd.concat([hastag["hastag_0"]], ignore_index=True)
    
        hastag = hastag.value_counts().head(10)
        logging.info('analyse_hastag data function call and return of data')
        return hastag
    except Exception as e:
        raise CustomException(e,sys)


def graph_sentiment(data):
    try:
        analys = data["Analysis"].value_counts().reset_index().sort_values(by="index", ascending=False)
        logging.info('sentimental data generated')

        return analys
    except Exception as e:
        raise CustomException(e,sys)

def cloud(data):
    try:
        text = " ".join(cat.split()[1] for cat in data)
        word_cloud = WordCloud(collocations = False, background_color = 'white').generate(text)
        logging.info('word cloud generate')
        return word_cloud
    except Exception as e:
        raise CustomException(e,sys)


       