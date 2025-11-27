import os
import requests
from io import BytesIO
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import textwrap
import urllib.parse
import random
import google.generativeai as genai

def generate_black_image(size=(1280, 720)):
    """Generates a plain black image."""
    return Image.new('RGB', size, color=(0, 0, 0))

import base64

def fetch_google_image(prompt, api_key):
    """Fetches an image using Google Imagen via REST API."""
    if not api_key:
        return None
        
    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-fast-generate-001:predict"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }
        data = {
            "instances": [
                {"prompt": prompt}
            ],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "16:9"
            }
        }
        
        print(f"Generating Google Image (REST) for: {prompt[:30]}...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            # The response format is usually: {'predictions': [{'bytesBase64Encoded': '...'}]}
            if 'predictions' in result and len(result['predictions']) > 0:
                prediction = result['predictions'][0]
                if 'bytesBase64Encoded' in prediction:
                    image_data = base64.b64decode(prediction['bytesBase64Encoded'])
                    return Image.open(BytesIO(image_data))
                elif 'mimeType' in prediction and 'bytesBase64Encoded' in prediction: # Some versions might wrap it
                     image_data = base64.b64decode(prediction['bytesBase64Encoded'])
                     return Image.open(BytesIO(image_data))
            
            print(f"Google Imagen unexpected response: {result}")
        else:
            print(f"Google Imagen API Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Google Imagen failed: {e}")
        return None

def fetch_ai_image(prompt, size=(1280, 720), api_key=None):
    """Fetches an AI generated image using Google Imagen."""
    if not api_key:
        return None

    print(f"Generating AI image for summary: {prompt[:50]}...")
    img = fetch_google_image(prompt, api_key)
    if img:
        return img.resize(size, Image.LANCZOS)
            
    return None

def create_text_overlay(text, base_image, size=(1280, 720)):
    """Overlays text on an image."""
    if base_image.size != size:
        base_image = base_image.resize(size)
    
    overlay = Image.new('RGBA', size, (0, 0, 0, 120))
    base_image = base_image.convert('RGBA')
    base_image = Image.alpha_composite(base_image, overlay)
    base_image = base_image.convert('RGB')
    
    d = ImageDraw.Draw(base_image)
    
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        font = ImageFont.load_default()

    lines = textwrap.wrap(text, width=50)
    line_height = 50
    total_height = len(lines) * line_height
    y_offset = (size[1] - total_height) // 2
    
    for line in lines:
        bbox = d.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x_offset = (size[0] - text_width) // 2
        
        d.text((x_offset + 2, y_offset + 2), line, font=font, fill=(0, 0, 0))
        d.text((x_offset, y_offset), line, font=font, fill=(255, 255, 255))
        y_offset += line_height
        
    return base_image

def fetch_article_image(url, size=(1280, 720)):
    """Fetches and resizes an image from a URL."""
    try:
        print(f"Fetching article image: {url}")
        # Disable SSL verification for image fetch as well
        response = requests.get(url, timeout=10, verify=False)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            return img.resize(size, Image.LANCZOS)
    except Exception as e:
        print(f"Error fetching article image {url}: {e}")
    return None

def generate_video(summary_text, api_key=None, article_images=None, output_path="news_summary.mp4"):
    """
    Generates a video from the summary text.
    """
    try:
        # 1. Generate Audio
        tts = gTTS(text=summary_text, lang='en')
        audio_path = "temp_audio.mp3"
        tts.save(audio_path)
        audio_clip = AudioFileClip(audio_path)

        # 2. Prepare Image Pool
        image_pool = []
        
        # A. Generate ONE AI Image for the whole story
        print("Generating 'Whole Story' AI Image...")
        # Create a prompt that summarizes the story for the image
        # We use the first 300 chars of the summary to avoid token limits but give enough context
        ai_prompt = f"A news illustration representing: {summary_text[:300]}"
        ai_img = fetch_ai_image(ai_prompt, api_key=api_key)
        if ai_img:
            image_pool.append(ai_img)
            print("Successfully added AI image to pool.")
        else:
            print("Failed to generate AI image.")

        # B. Process Article Images
        if article_images:
            print(f"Found {len(article_images)} article images. Verifying...")
            
            # Keywords to filter out irrelevant images
            ignore_terms = ["logo", "icon", "avatar", "profile", "ad-", "ads", "banner", "social", "footer", "header", "button", "tracker", "pixel", "share"]
            
            count = 0
            for url in article_images:
                if count >= 5: # Limit to 5 good images
                    break
                    
                # 1. URL Keyword Filter
                if any(term in url.lower() for term in ignore_terms):
                    continue
                
                # 2. Fetch and Dimension Check
                try:
                    # If it's the top image, we prioritize it, but still check if it's not a tiny icon
                    is_top_image = (url == article_images[0])
                    
                    temp_img = fetch_article_image(url)
                    if temp_img:
                        w, h = temp_img.size
                        
                        # Filter out small images
                        if w < 300 or h < 200:
                            print(f"Skipping small image: {url} ({w}x{h})")
                            continue
                            
                        # Filter out extreme aspect ratios (banners or skyscrapers)
                        aspect_ratio = w / h
                        if aspect_ratio > 3.0 or aspect_ratio < 0.3:
                            print(f"Skipping odd aspect ratio: {url} ({aspect_ratio:.2f})")
                            continue

                        # If we made it here, it's a valid image
                        image_pool.append(temp_img)
                        count += 1
                        print(f"Added article image to pool: {url}")
                    
                except Exception as e:
                    print(f"Error processing image {url}: {e}")
                    continue
        
        print(f"Total images in pool: {len(image_pool)}")

        # 3. Create Visuals
        sentences = [s.strip() for s in summary_text.split('.') if s.strip()]
        if len(sentences) < 2:
            sentences = [summary_text]
            
        clips = []
        duration_per_slide = audio_clip.duration / len(sentences)

        for i, sentence in enumerate(sentences):
            img = None
            
            # Pick image from pool
            if image_pool:
                # Cycle through the pool
                img = image_pool[i % len(image_pool)]
            
            # Fallback to Black
            if img is None:
                print("Pool empty. Using fallback black image.")
                img = generate_black_image()
                
                
            img_with_text = create_text_overlay(sentence, img)
            
            temp_img_path = f"temp_slide_{i}.png"
            img_with_text.save(temp_img_path)
            
            clip = ImageClip(temp_img_path).set_duration(duration_per_slide)
            clips.append(clip)
            
        final_video = concatenate_videoclips(clips)
        final_video = final_video.set_audio(audio_clip)
        
        final_video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
        
        final_video.close()
        audio_clip.close()
        if os.path.exists(audio_path):
            os.remove(audio_path)
        for i in range(len(sentences)):
            p = f"temp_slide_{i}.png"
            if os.path.exists(p):
                os.remove(p)
            
        return output_path
        
    except Exception as e:
        print(f"Error generating video: {e}")
        return None
