from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

def extract_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    
    Args:
        url (str): The YouTube URL.
        
    Returns:
        str: The video ID, or None if not found.
    """
    try:
        parsed_url = urlparse(url)
        if parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
        if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                p = parse_qs(parsed_url.query)
                return p['v'][0]
            if parsed_url.path[:7] == '/embed/':
                return parsed_url.path.split('/')[2]
            if parsed_url.path[:3] == '/v/':
                return parsed_url.path.split('/')[2]
        return None
    except Exception:
        return None

def get_video_transcript(video_id):
    """
    Fetches the transcript for a YouTube video.
    Tries to get English transcript first, then falls back to any available and translates to English.
    
    Args:
        video_id (str): The YouTube video ID.
        
    Returns:
        str: The transcript text, or None if an error occurs.
    """
    try:
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to get English transcript (manual or auto-generated)
            try:
                transcript = transcript_list.find_transcript(['en'])
            except Exception:
                # If no English, get the first available and translate to English
                try:
                    transcript = transcript_list.find_transcript(['en-US', 'en-GB'])
                except:
                    # Fallback to any transcript
                    transcript = next(iter(transcript_list))
                    if not transcript.is_translatable:
                         pass
                    else:
                        try:
                            transcript = transcript.translate('en')
                        except:
                            pass

            transcript_data = transcript.fetch()
        except AttributeError:
            # Fallback for instance-based API (non-standard library version)
            try:
                api = YouTubeTranscriptApi()
                if hasattr(api, 'fetch'):
                    transcript_obj = api.fetch(video_id)
                    # Handle FetchedTranscript object with snippets
                    if hasattr(transcript_obj, 'snippets'):
                        return " ".join([s.text for s in transcript_obj.snippets])
                    # Fallback if structure is different (e.g. list of dicts)
                    return " ".join([str(s) for s in transcript_obj])
            except Exception as inner_e:
                return f"Error using fallback method: {str(inner_e)}"

        transcript_text = " ".join([t['text'] for t in transcript_data])
        return transcript_text
    except Exception as e:
        return f"Error: {str(e)}"
