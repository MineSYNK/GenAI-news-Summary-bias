# 📰 News Summarizer & Bias Rater

A Streamlit application that scrapes news articles or YouTube video transcripts, summarizes them using Google Gemini AI, rates their bias, and optionally generates a short video summary.

## ✨ Features

*   **Article Scraping**: Automatically extracts text and images from news URLs.
*   **YouTube Support**: Fetches transcripts from YouTube videos for analysis.
*   **AI Analysis**: Uses Google Gemini to provide a 5-line summary and a bias rating (1-5).
*   **Video Generation**: Creates a short video summary with voiceover (TTS) and relevant images.
*   **Privacy Focused**: Your API keys are not stored and are only used for the current session.

## 🚀 How to Run

### Prerequisite: Google Gemini API Key
To use this app, you need a Google Gemini API key.
1.  Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Create a new API key.

### ⚠️ Important Note on Video Generation
**Video generation requires a paid Google Cloud project or a specific billing tier for the Gemini API.**
While text summarization works with the free tier, the image generation capabilities (Imagen) used for the video often require a billed account. If you are on the free tier, video generation may fail or return errors.

### Run Locally
1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the app:
    ```bash
    streamlit run app.py
    ```

### Deploy on Streamlit Cloud
1.  Fork this repository to your GitHub.
2.  Log in to [Streamlit Cloud](https://share.streamlit.io/).
3.  Create a new app and select your repository.
4.  Click **Deploy**.

## 🔑 API Key Usage & Privacy
*   The application requires you to enter your Google Gemini API Key in the sidebar.
*   **Your key is NOT stored** on the server or database.
*   It is only used temporarily within your active session to make requests to Google's servers for summarization and image generation.

## 🛠️ Technologies Used
*   **Streamlit**: UI Framework
*   **Google Gemini (Generative AI)**: LLM for summary and bias detection
*   **Newspaper3k**: Article scraping
*   **YouTube Transcript API**: Video transcript extraction
*   **MoviePy**: Video editing and creation
*   **gTTS**: Google Text-to-Speech
