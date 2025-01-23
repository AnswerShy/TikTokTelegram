import tempfile
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from io import BytesIO


def convert_time_to_seconds(time_str):
    import re
    match = re.match(r'(?:(\d+):)?(\d+):(\d+)(?:\.(\d+))?', time_str)
    if not match:
        raise ValueError("Invalid time format. Use HH:MM:SS.mmm or MM:SS.mmm or SS.mmm.")
    groups = match.groups()
    hours = int(groups[0]) if groups[0] else 0
    minutes = int(groups[1]) if groups[1] else 0
    seconds = int(groups[2]) if groups[2] else 0
    milliseconds = int(groups[3]) if groups[3] else 0
    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0


def trim_video(input_buffer, start_time, end_time):
    try:
        start_seconds = convert_time_to_seconds(start_time)
        end_seconds = convert_time_to_seconds(end_time)

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_input:
            temp_input.write(input_buffer.getvalue())
            temp_input_path = temp_input.name

        with VideoFileClip(temp_input_path) as clip:
            trimmed_clip = clip.subclip(start_seconds, end_seconds)

            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_output:
                trimmed_clip.write_videofile(temp_output.name, codec='libx264', audio_codec='aac')
                temp_output_path = temp_output.name

        with open(temp_output_path, 'rb') as output_file:
            output_buffer = BytesIO(output_file.read())

        os.remove(temp_input_path)
        os.remove(temp_output_path)

        return output_buffer

    except Exception as e:
        print(f"Failed to trim video: {e}")
        return None
