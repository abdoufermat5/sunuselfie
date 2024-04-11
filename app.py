import asyncio
import time
import random
import streamlit as st
import os
from datetime import datetime
import pandas as pd
from PIL import Image
from io import BytesIO
import requests
from dotenv import load_dotenv
from utils import fetch_tweets, is_woman, getAPI

load_dotenv()

getAPI()

st.set_page_config(page_title="Tendances Images et Vidéos", layout="wide")


async def main():
    # Check if the user is already logged in
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if not st.session_state['logged_in']:
        st.title("Page de connexion")
        st.sidebar.title("Connexion")
        username = st.sidebar.text_input("Username", placeholder="esprit_bayesien")
        email = st.sidebar.text_input("Email", placeholder="example@gmail.com")
        password = st.sidebar.text_input("Password", type="password", placeholder="password123")

        # save in st.session_state
        st.session_state["email"] = email
        st.session_state["password"] = password
        st.session_state["username"] = username

        # Display giant image in the center
        st.image(
            "https://vignette.wikia.nocookie.net/naruto/images/2/21/Profile_Jiraiya.PNG/revision/latest?cb=20160115173538",
            use_column_width=True)
        # display gif image

        if st.sidebar.button("Login"):

            # check if not empty fields
            if not username or not email or not password:
                st.error("Veuillez remplir tous les champs.")
            else:
                st.session_state['logged_in'] = True
                st.rerun()

    if st.session_state['logged_in']:
        # 3 seconds loading
        with st.spinner("Chargement des données..."):
            st.image("https://64.media.tumblr.com/c607336006510969a61b2fa8721f8ba3/tumblr_n17plqQM0w1sji00bo1_500.gif",
                     use_column_width=True)
            time.sleep(3)
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

        st.sidebar.title("Paramètres de recherche")
        currentYear = datetime.now().year
        st.title(f"Sunuselfie Korité/Tabaski {currentYear} [optionnel]")

        # input list of queries to search for
        q_list = st.sidebar.text_input("Liste de filters", value=f"#sunuselfiekorite{currentYear}, sunuselfie")

        count = st.sidebar.number_input("Nombre de tweets", min_value=10, value=150, step=10)
        min_retweets = st.sidebar.number_input("Nombre minimal de retweets", min_value=50, value=150, step=10)
        date_since = st.sidebar.date_input("Date de début",
                                           # value 5 days ago
                                           value=datetime.now().date() - pd.Timedelta(days=1),
                                           # min value 1 week ago
                                           min_value=datetime.now().date() - pd.Timedelta(days=7),
                                           # max value today
                                           max_value=datetime.now().date())
        date_until = st.sidebar.date_input("Date de fin",
                                           # value today
                                           value=datetime.now().date(),
                                           # min value 1 week ago
                                           min_value=datetime.now().date() - pd.Timedelta(days=7),
                                           # max value today
                                           max_value=datetime.now().date())
        # convert date to string like "2024-04-10"
        date_since = date_since.strftime("%Y-%m-%d")
        date_until = date_until.strftime("%Y-%m-%d")
        q = q_list.split(",")
        gender_detect = st.sidebar.checkbox("Détecter les femmes (💀💀💀💀)", value=False)

        tabs = ["Images", "Vidéos"]
        tab = st.selectbox("Choisissez un onglet", tabs)

        tweets = await fetch_tweets(q, count, date_since, date_until, min_retweets, credentials={
            "username": st.session_state["username"],
            "password": st.session_state["password"],
            "email": st.session_state["email"],
            "email_password": st.session_state["password"]
        })

        if tab == "Images":
            st.subheader("Images yii")

            images = []
            only_girls = []
            temp_dir = "temp"
            for tweet in tweets:
                if "media" in tweet:

                    if tweet["media"]["photos"]:
                        for photo in tweet["media"]["photos"]:
                            img_url = photo["url"]

                            username = tweet['user']['displayname']
                            tweet_url = f"https://twitter.com/{username}/status/{tweet['id']}"
                            images.append((tweet['date'], img_url, username, tweet_url))

            if gender_detect:
                for date, img_url, username, tweet_url in images:
                    img_content = Image.open(BytesIO(requests.get(img_url).content))

                    # Create a temporary directory to store the temporary files

                    if not os.path.exists(temp_dir):
                        os.makedirs(temp_dir)

                    # Save PIL image to a temporary file
                    temp_img_filename = os.path.join(temp_dir, f"temp_img{random.randint(0, 100000)}.jpg")
                    img_content.save(temp_img_filename, "JPEG")
                    a_woman = is_woman(temp_img_filename)
                    if a_woman:
                        only_girls.append((date, img_url, username, tweet_url))
                print("only girls #######", len(only_girls))

            for username, group in pd.DataFrame(images if not gender_detect else only_girls,
                                                columns=["Date", "Image", "Username", "Tweet URL"]).sort_values(
                    by="Date", ascending=False).groupby(by="Username"):
                st.markdown(f"<hr><h2 style='text-align:center'>Photos de {username}</h2>",
                            unsafe_allow_html=True)
                for index, (img, date, tweet_url) in group[["Image", "Date", "Tweet URL"]].iterrows():
                    # draw a grey zigzag line
                    st.markdown(
                        "<div style='background-color: #f0f2f6; padding: .15em; border-radius: 8px;'><hr></div>",
                        unsafe_allow_html=True)

                    st.write(f"{date.strftime('%Y-%m-%d à %H:%M:%S')}")
                    st.image(img, width=200, use_column_width=True, output_format="JPEG")
                    st.markdown(f"<a href='{tweet_url}' target='_blank'>Voir sur Twitter</a>", unsafe_allow_html=True)

                    st.markdown("<br/>", unsafe_allow_html=True)

        elif tab == "Vidéos":
            st.subheader("Vidéos yii")

            videos = []
            for tweet in tweets:
                if "media" in tweet:

                    if tweet["media"]["videos"]:
                        for video in tweet["media"]["videos"]:
                            video_url = video["variants"][0]["url"]
                            tweet_url = f"https://twitter.com/{tweet['user']['displayname']}/status/{tweet['id']}"
                            videos.append((tweet["date"], video_url, tweet_url))

            for date, group in pd.DataFrame(videos, columns=["Date", "Video", "Url"]).groupby("Date"):
                st.write(f"{date.strftime('%Y-%m-%d %H:%M:%S')}")
                for id, (video_url, tweet_url) in group[["Video", "Url"]].iterrows():
                    st.video(video_url)
                    st.markdown("<br/>", unsafe_allow_html=True)
                    st.markdown(f"<a href='{tweet_url}' target='_blank'>Voir sur Twitter</a>", unsafe_allow_html=True)


if __name__ == "__main__":
    asyncio.run(main())
