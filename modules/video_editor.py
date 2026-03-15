import os
import requests
from moviepy.editor import (
    AudioFileClip, 
    VideoFileClip, 
    TextClip, 
    CompositeVideoClip, 
    concatenate_videoclips
)
from config import TEMP_FOLDER

def download_file(url, filename):
    try:
        with open(filename, 'wb') as f:
            f.write(requests.get(url).content)
        return True
    except Exception as e:
        print(f"Download Error: {e}")
        return False

def create_video(script_text, audio_path, media_urls, output_filename):
    # 1. Load Audio
    try:
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration # e.g., 60 seconds
    except:
        raise ValueError("Could not load audio.")

    if not media_urls:
        raise ValueError("No video clips found.")
    
    # 2. Logic: How long should each clip be?
    # We want fast cuts (e.g., every 5 seconds) to keep it engaging.
    target_clip_duration = 5.0 
    
    clips = []
    current_duration = 0
    media_index = 0
    
    # 3. Build the video loop until we match audio duration
    while current_duration < audio_duration:
        # Cycle through the media files we have
        vid_url = media_urls[media_index % len(media_urls)]
        media_index += 1
        
        local_vid_path = os.path.join(TEMP_FOLDER, f"clip_{media_index}.mp4")
        
        if not download_file(vid_url, local_vid_path):
            continue

        try:
            video_clip = VideoFileClip(local_vid_path).without_audio().resize(width=1280)
            
            # Determine how much time is left to fill
            time_left = audio_duration - current_duration
            
            # Use the shorter of: target duration (5s) OR time left
            this_clip_duration = min(target_clip_duration, time_left)
            
            # Handle source clip length
            if video_clip.duration < this_clip_duration:
                # If source is too short, loop it
                video_clip = video_clip.loop(duration=this_clip_duration)
            else:
                # Cut a random segment or the start
                video_clip = video_clip.subclip(0, this_clip_duration)
            
            video_clip = video_clip.set_duration(this_clip_duration)
            clips.append(video_clip)
            current_duration += this_clip_duration
            
        except Exception as e:
            print(f"Clip Error: {e}")
            
    # 4. Final Assembly
    if clips:
        final_video = concatenate_videoclips(clips, method="compose")
        final_video = final_video.set_audio(audio_clip)
        
        # Add subtitles (Optional, simple centered text)
        # Note: Complex subtitles require ImageMagick. If it fails, we skip text.
        try:
           # (We skip text here to ensure video renders 100% of the time for now)
           pass 
        except:
           pass

        final_video.write_videofile(
            output_filename, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            preset='ultrafast'
        )
        return output_filename
    else:
        raise ValueError("Video creation failed.")