import streamlit as st
import tweepy as tw
from helper import preprocessing_data,graph_sentiment,analyse_hastag,mention_data,download_data,cloud
from helper import api
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from src.exeption import CustomException
import sys


st.set_page_config(
    page_title="Twitter data Visulization",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/prasantpoudel/twitter_sentimental',
        'Report a bug': "https://github.com/prasantpoudel/twitter_sentimental/issues",
    }
)

st.title("Twitter Sentimental Analysis")
option = st.selectbox(
    'Search By',
    ('Name','hashtag'))

if option=="Name":
    query=st.text_input("Enter the username (don't include @)")
if option=="hashtag":
    query=st.text_input("Enter the hashtag (don't include #)")

tweet_number=st.number_input('Insert a number(default is 50)',min_value=3, max_value=1000,value=3,label_visibility='visible')

if st.button("Analysis Sentiment"):
    data=preprocessing_data(query,tweet_number,option)
    analyse = graph_sentiment(data)
    mention = mention_data(data)
    hastag = analyse_hastag(data)

    st.write(" ")
    st.write(" ")
    st.header("Extracted and Preprocessed Dataset")
    st.write(data)
    download_data(data, label="twitter_sentiment_filtered")
    st.write(" ")
    
    col1, col2, col3 = st.columns(3)
    with col2:
        st.markdown("### EDA On the Data")


    col1, col2 = st.columns(2)

    with col1:
        st.text("Top 10 @Mentions in {} tweets".format(tweet_number))
        st.bar_chart(mention)
    with col2:
        st.text("Top 10 Hastags used in {} tweets".format(tweet_number))
        st.bar_chart(hastag)
    
    col3, col4 = st.columns(2)
    with col3:
        st.text("Top 10 Used Links for {} tweets".format(tweet_number))
        st.bar_chart(data["links"].value_counts().head(10).reset_index())
    
    with col4:
        st.text("All the Tweets that containes top 10 links used")
        filtered_data = data[data["links"].isin(data["links"].value_counts().head(10).reset_index()["index"].values)]
        st.write(filtered_data)

    col5,col6=st.columns(2)
    with col5:
        st.text("Twitter Sentment Analysis")
        st.bar_chart(analyse)

    with col6:
        st.text("word cloud")
        wordcloud=cloud(data['Tweets'])
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.show()
    



