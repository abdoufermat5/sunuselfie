import asyncio

from deepface import DeepFace
from twscrape import API, gather
import cv2
import streamlit as st
import os
import math

from detect_face import detect_faces


def getAPI():
    # delete the `path-to.db` if you want to use the default `accounts.db`
    return API()


def check_credentials_on_os():
    username = os.getenv("username")
    password = os.getenv("password")
    email = os.getenv("email")

    if username and password and email:
        return {"username": username, "password": password, "email": email}
    return False


async def login(username="", password="", email="", email_password=""):
    api = getAPI()  # or API("path-to.db") - default is `accounts.db`

    await api.pool.add_account(username, password, email, email_password)
    c = await api.pool.login(username)
    print(c)
    if c["success"]==0:
        # try relogin
        await api.pool.relogin(username)
    return api


def sync_login(u, p, e, ep):
    asyncio.run(login(u, p, e, ep))
    return True


async def fetch_tweets(q: list = None, count=100, date_since="2024-04-10", date_until="2024-04-11",
                       min_retweets=0, credentials: dict = None):
    if q is None:
        q = ["#sunuselfiekorite2024", "sunuselfie"]
    all_tweets = []
    api = await login(**credentials)
    # span queries with OR
    span_q = " OR ".join(q) if len(q) > 1 else q[0]

    queries = f"({span_q}) since:{date_since} until:{date_until} -filter:retweets"
    try:
        all_tweets = await gather(api.search(queries, limit=count, kv={"product": "Media"}))
    except Exception as e:
        st.error(f"Erreur lors de la récupération des tweets : {e}")
    all_tweets = [tweet.dict() for tweet in all_tweets if tweet.retweetCount >= min_retweets]
    return all_tweets


def sync_fetch_tweets(h, c, dt, mr, credentials):
    return asyncio.run(fetch_tweets(h, c, dt, mr, credentials))


def is_woman(image_path):
    # first try
    percent = 0

    result = DeepFace.analyze(img_path=image_path, actions=["gender"], enforce_detection=False)
    print(result)
    percent = float(result[0]["gender"]["Woman"])
    if percent > 30:
        # delete image
        if os.path.exists(image_path):
            os.remove(image_path)
        return True
    # second try
    else:
        faces = detect_faces(image_path, display=False, output_path="./temp/Extracted")
        gender_results = []
        for face in faces:
            path = os.path.join("./temp/Extracted", face)
            result = DeepFace.analyze(img_path=path, actions=["gender"], enforce_detection=False)
            print(result)
            gender_results.append(float(result[0]["gender"]["Woman"]))
        # delete the extracted faces
        for face in faces:
            path = os.path.join("./temp/Extracted", face)
            if os.path.exists(path):
                os.remove(path)

        # delete image
        if os.path.exists(image_path):
            os.remove(image_path)
        if len(gender_results)>0:
            return sum(gender_results)/len(gender_results) > 30
        return False


