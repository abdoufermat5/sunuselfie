import os
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from io import BytesIO

import requests
import streamlit as st
import tweepy
from PIL import Image
from deepface import DeepFace
from dotenv import load_dotenv

load_dotenv()

# Twitter API credentials
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

# Authenticate to the Twitter API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


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


def fetch_images(hashtags, count, start_date, end_date):
    end_date = end_date + timedelta(days=1)  # Include tweets from the end_date

    # split hashtags by space and join with OR

    hashtags = " OR ".join(hashtags.split())
    # query that fetches tweets with media or images from the given date range
    queries = f"{hashtags} -filter:retweets filter:media"
    tweets = tweepy.Cursor(api.search_tweets, q=queries, tweet_mode="extended", since=start_date, until=end_date, include_entities=True).items(count)

    images_by_hour = defaultdict(list)
    user_image_count = defaultdict(int)

    for tweet in tweets:
        if 'media' in tweet.entities:
            for media in tweet.entities['media']:
                # Add a new condition to handle video media types
                if media['type'] == 'video' or media['type'] == 'animated_gif':
                    video_info = media['video_info']
                    video_variants = video_info['variants']
                    max_bitrate = -1
                    video_url = ''
                    for variant in video_variants:
                        if variant['content_type'] == 'video/mp4' and variant['bitrate'] > max_bitrate:
                            max_bitrate = variant['bitrate']
                            video_url = variant['url']

                    if video_url:
                        tweet_hour = tweet.created_at.strftime('%Y-%m-%d %H:00')
                        images_by_hour[tweet_hour].append(
                            {'video_url': video_url, 'user': tweet.user.screen_name})

                elif media['type'] == 'photo':
                    img_url = media['media_url_https']
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
                        tweet_hour = tweet.created_at.strftime('%Y-%m-%d %H:00')
                        images_by_hour[tweet_hour].append(
                            {'image': img_content, 'user': tweet.user.screen_name, 'gender': gender})

                    # Increment the count of images fetched for the user
                    user_image_count[tweet.user.screen_name] += 1

    return images_by_hour


def display_images(images_by_hour):
    for hour, images in sorted(images_by_hour.items()):
        st.header(f"Date: {hour}")
        cols = st.columns(4)
        for img_data in images:
            user = img_data['user']
            index = images.index(img_data) % 4
            with cols[index].container():
                if 'image' in img_data:
                    img = img_data['image']
                    st.image(img, use_column_width=True, caption=f"{user}")
                elif 'video_url' in img_data:
                    print("VIDEOOOOOOOOOOOOOOO")
                    video_url = img_data['video_url']
                    st.video(video_url, caption=f"{user}")


def main():
    hashtag = st.text_input("Enter the hashtag to fetch images:", "#sunuselfiekorite #sunukorite #sunuselfiekorite2023")
    fetch_count = st.number_input("Number of tweets to fetch:", min_value=10, max_value=500, value=10, step=10)
    start_date = st.date_input("Select the start date for tweets:", datetime.now() - timedelta(days=7))
    end_date = st.date_input("Select the end date for tweets:", datetime.now())
    if st.button("Fetch Images"):
        # loader
        with st.spinner("Fetching images..."):
            images_by_hour = fetch_images(hashtag, fetch_count, start_date, end_date)
            display_images(images_by_hour)
    else:
        st.write("Enter a hashtag and click 'Fetch Images' to display images.")


if __name__ == "__main__":
    st.set_page_config(page_title="Twitter Image Fetcher", layout="wide", initial_sidebar_state="collapsed")
    main()
