# python movie_trim.py split input_video.mp4 00:02:00
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
import argparse

def time_to_seconds(time_str):
    parts = list(map(float, time_str.split(':')))
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h, m, s = 0, parts[0], parts[1]
    else:
        raise ValueError("Invalid time format. Use HH:MM:SS or MM:SS.")
    return h * 3600 + m * 60 + s

def trim_video(filename, start_time, end_time, output_filename):
    if not os.path.exists(filename):
        print(f"Error: The file {filename} does not exist.")
        return

    start_time = time_to_seconds(start_time)
    end_time = time_to_seconds(end_time)
    print(f'filename: {filename}  start_time:{start_time} end_time:{end_time}')
    try:
        with VideoFileClip(filename) as video:
            trimmed_video = video.subclip(start_time, end_time)
            trimmed_video.write_videofile(output_filename, codec="libx264")
            print(f"Trimmed video saved as {output_filename}")
    except OSError as e:
        print(f"Error: {e}")
        print("Files in the current directory:")
        for file in os.listdir('.'):
            print(file)

def concatenate_videos(filename1, filename2, output_filename):
    if not os.path.exists(filename1):
        print(f"Error: The file {filename1} does not exist.")
        return
    if not os.path.exists(filename2):
        print(f"Error: The file {filename2} does not exist.")
        return

    try:
        with VideoFileClip(filename1) as video1, VideoFileClip(filename2) as video2:
            final_video = concatenate_videoclips([video1, video2])
            final_video.write_videofile(output_filename, codec="libx264")
            print(f"Concatenated video saved as {output_filename}")
    except OSError as e:
        print(f"Error: {e}")
        print("Files in the current directory:")
        for file in os.listdir('.'):
            print(file)

def add_audio_to_video(video_filename, audio_filename, output_filename):
    if not os.path.exists(video_filename):
        print(f"Error: The file {video_filename} does not exist.")
        return
    if not os.path.exists(audio_filename):
        print(f"Error: The file {audio_filename} does not exist.")
        return

    try:
        with VideoFileClip(video_filename) as video:
            audio = AudioFileClip(audio_filename)
            video_with_audio = video.set_audio(audio)
            video_with_audio.write_videofile(output_filename, codec="libx264")
            print(f"Video with new audio saved as {output_filename}")
    except OSError as e:
        print(f"Error: {e}")
        print("Files in the current directory:")
        for file in os.listdir('.'):
            print(file)

def split_video(filename, split_duration):
    if not os.path.exists(filename):
        print(f"Error: The file {filename} does not exist.")
        return

    try:
        with VideoFileClip(filename) as video:
            video_duration = video.duration
            split_duration = time_to_seconds(split_duration)
            for start_time in range(0, int(video_duration), int(split_duration)):
                end_time = min(start_time + split_duration, video_duration)
                output_filename = f"{os.path.splitext(filename)[0]}_part{start_time // split_duration + 1}.mp4"
                video.subclip(start_time, end_time).write_videofile(output_filename, codec="libx264")
                print(f"Created {output_filename}")
    except OSError as e:
        print(f"Error: {e}")
        print("Files in the current directory:")
        for file in os.listdir('.'):
            print(file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trim, concatenate, split videos, or add audio to a video.")
    subparsers = parser.add_subparsers(dest="command")

    trim_parser = subparsers.add_parser("trim", help="Trim a video from start time to end time.")
    trim_parser.add_argument("filename", help="The name of the file to process.")
    trim_parser.add_argument("start", help="The start time in HH:MM:SS or MM:SS format.")
    trim_parser.add_argument("end", help="The end time in HH:MM:SS or MM:SS format.")
    trim_parser.add_argument("output", help="The name of the output file.")

    concat_parser = subparsers.add_parser("concat", help="Concatenate two videos.")
    concat_parser.add_argument("filename1", help="The name of the first file to process.")
    concat_parser.add_argument("filename2", help="The name of the second file to process.")
    concat_parser.add_argument("output", help="The name of the output file.")

    audio_parser = subparsers.add_parser("add_audio", help="Add a WAV file to the sound of the video.")
    audio_parser.add_argument("video_filename", help="The name of the video file to process.")
    audio_parser.add_argument("audio_filename", help="The name of the audio file to add.")
    audio_parser.add_argument("output", help="The name of the output file.")

    split_parser = subparsers.add_parser("split", help="Split a video into multiple parts.")
    split_parser.add_argument("filename", help="The name of the file to process.")
    split_parser.add_argument("duration", help="The duration of each split part in HH:MM:SS or MM:SS format.")

    args = parser.parse_args()

    if args.command == "trim":
        trim_video(args.filename, args.start, args.end, args.output)
    elif args.command == "concat":
        concatenate_videos(args.filename1, args.filename2, args.output)
    elif args.command == "add_audio":
        add_audio_to_video(args.video_filename, args.audio_filename, args.output)
    elif args.command == "split":
        split_video(args.filename, args.duration)