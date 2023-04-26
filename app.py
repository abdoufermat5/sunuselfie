import streamlit as st
import tweepy
import os
from tweepy import API
from datetime import datetime
import pandas as pd
from deepface import DeepFace
from PIL import Image
from io import BytesIO
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

# Twitter API credentials
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

# Authentification Twitter API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


@st.cache_data()
def fetch_tweets(hashtags="#sunuselfiekorite2023", count=100, date_since=datetime.now().strftime("%Y-%m-%d"),
                 min_retweets=0):
    # get timestamp date
    # date_since = datetime.strptime(date_since, "%Y-%m-%d").timestamp()
    hashtags = f"{hashtags} filter:media -filter:retweets"
    try:
        tweets = tweepy.Cursor(api.search_tweets, q=hashtags, since_id=date_since, tweet_mode="extended",
                               include_entities=True).items(count)
        return [tweet for tweet in tweets if tweet.retweet_count >= min_retweets]
    except Exception as e:
        st.error(f"Erreur lors de la récupération des tweets : {e}")
        return []


def detect_gender(image):
    try:
        result = DeepFace.analyze(img_path=image, actions=['gender'], enforce_detection=False)

        woman_detected = False
        if isinstance(result, list):
            # Handle cases with multiple detected faces
            for face_result in result:
                if face_result['gender']['Woman'] > 50:
                    woman_detected = True
                    break
        else:
            if result['gender']['Woman'] > 50:
                woman_detected = True

    except ValueError as e:
        print("Warning:", e)
        woman_detected = False

    return woman_detected


st.set_page_config(page_title="Tendances Images et Vidéos", layout="wide")

# CSS styles
st.markdown("""
    <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }

        .stButton>button {
            background-color: #2f80ed;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            border: none;
            padding: 0.5em 1em;
            margin-top: 1em;
            margin-right: 1em;
            transition: all 0.2s ease-in-out;
            box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.25);
        }

        .stButton>button:hover {
            background-color: #2f80edcc;
            cursor: pointer;
        }

        .stTextInput>div>div>input {
            background-color: #f0f2f6;
            color: #333333;
            border-radius: 8px;
            border: none;
            padding: 0.5em 1em;
            transition: all 0.2s ease-in-out;
            box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.25);
            width: 100%;
        }

        .stTextInput>div>div>input:focus {
            background-color: white;
            box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
        }

        .stNumberInput>div>div>div>input {
            background-color: #f0f2f6;
             color: #333333;
        border-radius: 8px;
        border: none;
        padding: 0.5em 1em;
        transition: all 0.2s ease-in-out;
        box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.25);
        width: 100%;
    }

    .stNumberInput>div>div>div>input:focus {
        background-color: white;
        box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
    }

    .stDateInput>div>div>input {
        background-color: #f0f2f6;
        color: #333333;
        border-radius: 8px;
        border: none;
        padding: 0.5em 1em;
        transition: all 0.2s ease-in-out;
        box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.25);
        width: 100%;
    }

    .stDateInput>div>div>input:focus {
        background-color: white;
        box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
    }

    .stVideo>div>video {
        border-radius: 8px;
        box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.25);
        max-width: 100%;
    }

    .stImage>div>img {
        border-radius: 8px;
        box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.25);
        max-width: 100%;
        background-color: #f0f2f6;
        padding: 1em;
    }

    .stMarkdown>div>p:first-child {
        font-size: 2rem;
        font-weight: bold;
        margin-top: 1em;
        margin-bottom: 0.5em;
    }

    .stMarkdown>div>div>img {
        border-radius: 8px;
        box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.25);
        max-width: 100%;
        margin-top: 1em;
        margin-bottom: 1em;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Tendances Images et Vidéos")
st.sidebar.title("Paramètres de recherche")

hashtags = st.sidebar.text_input("Hashtags", value="#sunuselfiekorite2023")
count = st.sidebar.number_input("Nombre de tweets", min_value=10, value=50, step=10)
min_retweets = st.sidebar.number_input("Nombre minimal de retweets", min_value=50, value=50, step=50)
date_since = st.sidebar.date_input("Date de début",
                                   # value 5 days ago
                                   value=datetime.now().date() - pd.Timedelta(days=5),
                                   # min value 1 week ago
                                   min_value=datetime.now().date() - pd.Timedelta(days=7),
                                   # max value today
                                   max_value=datetime.now().date())

tabs = ["Images", "Vidéos"]
tab = st.selectbox("Choisissez un onglet", tabs)

tweets = fetch_tweets(hashtags, count, date_since, min_retweets)

if tab == "Images":
    st.subheader("Images en tendances")

    images = []
    for tweet in tweets:
        if "media" in tweet.entities:
            for media in tweet.extended_entities["media"]:
                if media["type"] == "photo":
                    img_url = media["media_url_https"]
                    img_content = Image.open(BytesIO(requests.get(img_url).content))

                    # Create a temporary directory to store the temporary files
                    temp_dir = "temp"
                    if not os.path.exists(temp_dir):
                        os.makedirs(temp_dir)

                    # Save PIL image to a temporary file
                    temp_img_filename = os.path.join(temp_dir, "temp_img.jpg")
                    img_content.save(temp_img_filename, "JPEG")
                    gender = detect_gender(temp_img_filename)
                    os.remove(temp_img_filename)  # Delete the temporary file after processing

                    if gender:
                        username = tweet.user.screen_name
                        tweet_url = f"https://twitter.com/{username}/status/{tweet.id}"
                        images.append((tweet.created_at.date(), img_content, username, tweet_url))

    for date, group in pd.DataFrame(images, columns=["Date", "Image", "Username", "Tweet URL"]).groupby("Date"):
        st.markdown(f"<hr><h2 style='text-align:center'>Date: {date.strftime('%Y-%m-%d')}</h2>", unsafe_allow_html=True)
        for index, (img, username, tweet_url) in group[["Image", "Username", "Tweet URL"]].iterrows():
            # draw a grey zigzag line
            st.markdown("<div style='background-color: #f0f2f6; padding: .15em; border-radius: 8px;'><hr></div>",
                        unsafe_allow_html=True)

            st.markdown(f"<h3>{username}</h3>", unsafe_allow_html=True)
            st.image(img, width=200, use_column_width=True, output_format="JPEG")
            st.markdown(f"<a href='{tweet_url}' target='_blank'>Voir sur Twitter</a>", unsafe_allow_html=True)

            st.markdown("<br/>", unsafe_allow_html=True)

elif tab == "Vidéos":
    st.subheader("Vidéos en tendances")

    videos = []
    for tweet in tweets:
        if "media" in tweet.entities:
            for media in tweet.entities["media"]:
                if media["type"] == "video":
                    video_url = media["video_info"]["variants"][0]["url"]
                    videos.append((tweet.created_at.date(), video_url))

    for date, group in pd.DataFrame(videos, columns=["Date", "Video"]).groupby("Date"):
        st.markdown(f"<hr><h2 style='text-align:center'>{date.strftime('%Y-%m-%d')}</h2>", unsafe_allow_html=True)
        for _, video_url in group["Video"].iteritems():
            st.video(video_url)
