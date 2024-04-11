import asyncio

from deepface import DeepFace
from twscrape import API, gather
from datetime import datetime
import streamlit as st
import os


def getAPI():
    # delete the `path-to.db` if you want to use the default `accounts.db`
    existing = "./accounts.db"
    if os.path.exists(existing):
        os.remove(existing)
    return API()


async def login(username="", password="", email="", email_password=""):
    api = getAPI()  # or API("path-to.db") - default is `accounts.db`

    await api.pool.add_account(username, password, email, email_password)
    await api.pool.login_all()

    return api


def sync_login(u, p, e, ep):
    asyncio.run(login(u, p, e, ep))
    return True


async def fetch_tweets(hashtags="#sunuselfiekorite2024", count=100, date_since=datetime.now().strftime("%Y-%m-%d"),
                       min_retweets=0, credentials: dict = None):
    all_tweets = []
    api = await login(**credentials)
    # get timestamp date
    # date_since = datetime.strptime(date_since, "%Y-%m-%d").timestamp()
    hashtags = f"{hashtags} filter:media -filter:retweets"
    try:

        all_tweets = await gather(api.search(hashtags, limit=count, kv={"product": "Top"}))
    except Exception as e:
        st.error(f"Erreur lors de la récupération des tweets : {e}")
    all_tweets = [tweet.dict() for tweet in all_tweets if tweet.retweetCount >= min_retweets]
    return all_tweets


def sync_fetch_tweets(h, c, dt, mr, credentials):
    return asyncio.run(fetch_tweets(h, c, dt, mr, credentials))


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
