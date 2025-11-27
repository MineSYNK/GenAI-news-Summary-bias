import requests
import streamlit as st
import random
import string

def get_notification_topic():
    """
    Gets the ntfy.sh topic from Streamlit secrets or generates a random one if not set.
    """
    if "NTFY_TOPIC" in st.secrets:
        return st.secrets["NTFY_TOPIC"]
    
    # Fallback to a default or random topic if not configured
    # Ideally, the user should configure this to receive notifications reliably.
    return "news-scraper-visits-default"

def send_notification(message):
    """
    Sends a notification to ntfy.sh.
    """
    topic = get_notification_topic()
    try:
        requests.post(f"https://ntfy.sh/{topic}", 
                      data=message.encode(encoding='utf-8'),
                      headers={
                          "Title": "News Scraper Visit",
                          "Priority": "default",
                          "Tags": "newspaper"
                      })
    except Exception as e:
        print(f"Failed to send notification: {e}")
