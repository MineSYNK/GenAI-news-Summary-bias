import google.generativeai as genai
import os

def analyze_article(text, api_key):
    """
    Analyzes the article text to provide a summary and bias rating.
    
    Args:
        text (str): The text content of the article.
        api_key (str): The Google Gemini API key.
        
    Returns:
        dict: A dictionary containing 'summary' and 'bias_rating'.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        You are a helpful news analyst. Please perform the following two tasks on the provided text (which may be a news article or a video transcript):
        
        1. Summarize the news in exactly 5 lines.
        2. Rate it in terms of bias on a scale of 1 to 5, where 1 is neutral and 5 is very biased. Provide only the number.
        
        Format the output exactly as follows:
        Summary:
        [Line 1]
        [Line 2]
        [Line 3]
        [Line 4]
        [Line 5]
        
        Bias Rating: [Rating]
        
        Article Text:
        {text}
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error analyzing article: {e}"
