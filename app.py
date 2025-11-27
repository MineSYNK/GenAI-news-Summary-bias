import streamlit as st
import re
from scraper import scrape_article
from analyzer import analyze_article
from youtube_utils import extract_video_id, get_video_transcript
from video_generator import generate_video
from utils import send_notification
import os

st.set_page_config(page_title="News Summarizer & Bias Rater", page_icon="📰")

st.title("📰 News Summarizer & Bias Rater")

with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter Google Gemini API Key", type="password")
    st.markdown("[Get your API key here](https://aistudio.google.com/app/apikey)")
    
    st.info("Your API key is used locally for this session and is not stored.")

url = st.text_input("Enter News Article or YouTube URL", placeholder="https://example.com/news-article or https://youtube.com/watch?v=...")

if st.button("Analyze"):
    if not api_key:
        st.error("Please enter your Google Gemini API Key in the sidebar.")
    elif not url:
        st.error("Please enter a URL.")
    else:
        article_text = None
        video_id = extract_video_id(url)
        
        if video_id:
            with st.spinner("Fetching YouTube transcript..."):
                transcript_result = get_video_transcript(video_id)
                if transcript_result and transcript_result.startswith("Error:"):
                    st.error(f"Could not retrieve transcript. Details: {transcript_result}")
                elif not transcript_result:
                    st.error("Could not retrieve transcript. Unknown error.")
                else:
                    article_text = transcript_result
        else:
            with st.spinner("Scraping article..."):
                scrape_result = scrape_article(url)
                if scrape_result:
                    article_text, top_image, article_images = scrape_result
                    
                    # Prioritize top_image
                    final_images = []
                    if top_image:
                        final_images.append(top_image)
                    
                    # Add other images
                    if article_images:
                        final_images.extend(article_images)
                        
                    st.session_state['article_images'] = final_images
                else:
                    article_text = None
                    st.error("Failed to scrape the article. Please check the URL.")
            
        if article_text:
            with st.spinner("Analyzing content..."):
                # Pass the user-provided api_key
                result = analyze_article(article_text, api_key)
                st.markdown(result)
                
                # Extract summary for video generation
                try:
                    summary_match = re.search(r"Summary:\s*(.*?)\s*Bias Rating:", result, re.DOTALL)
                    if summary_match:
                        summary_text = summary_match.group(1).strip()
                        
                        # Store summary in session state to persist across reruns (button clicks)
                        st.session_state['summary_text'] = summary_text
                        
                        # Send notification
                        try:
                            notification_msg = f"New Analysis:\nURL: {url}\nSummary: {summary_text[:100]}..."
                            send_notification(notification_msg)
                        except Exception as e:
                            print(f"Notification error: {e}")
                            
                except Exception as e:
                    st.warning(f"Could not parse summary for video generation: {e}")

# Display Generate Video button if summary is available
if 'summary_text' in st.session_state:
    if st.button("Generate Video Summary"):
        if not api_key:
             st.error("Please enter your API Key to generate video.")
        else:
            with st.spinner("Generating video (this may take a moment)..."):
                # Get images if they exist
                images = st.session_state.get('article_images', [])
                # Pass the user-provided api_key
                video_path = generate_video(st.session_state['summary_text'], api_key=api_key, article_images=images)
                if video_path:
                    st.video(video_path)
                    st.success("Video generated successfully!")
                    
                    # Add Download Button
                    with open(video_path, "rb") as file:
                        btn = st.download_button(
                            label="Download Video",
                            data=file,
                            file_name="news_summary.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("Failed to generate video.")
