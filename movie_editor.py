import os
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
import argparse
from typing import Union

def time_to_seconds(time_str: str) -> int:
    """Convert time string in HH:MM:SS or MM:SS format to seconds."""
    parts = list(map(float, time_str.split(':')))
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h, m, s = 0, parts[0], parts[1]
    else:
        raise ValueError("Invalid time format. Use HH:MM:SS or MM:SS.")
    return int(h * 3600 + m * 60 + s)

def check_file_exists(filename: str) -> bool:
    """Check if a file exists."""
    if not os.path.exists(filename):
        print(f"Error: The file {filename} does not exist.")
        return False
    return True

def handle_error(e: Exception) -> None:
    """Handle errors by printing the error message and listing files in the current directory."""
    print(f"Error: {e}")
    print("Files in the current directory:")
    for file in os.listdir('.'):
        print(file)

def write_video(video, output_filename: str) -> None:
    """Write the video to a file."""
    video.write_videofile(output_filename, codec="libx264")
    print(f"Video saved as {output_filename}")

def trim_video(filename: str, start_time: str, end_time: str, output_filename: str) -> None:
    """Trim a video from start time to end time."""
    if not check_file_exists(filename):
        return
    
    start_time_sec, end_time_sec = time_to_seconds(start_time), time_to_seconds(end_time)
    try:
        with VideoFileClip(filename) as video:
            write_video(video.subclip(start_time_sec, end_time_sec), output_filename)
    except OSError as e:
        handle_error(e)

def concatenate_videos(filename1: str, filename2: str, output_filename: str) -> None:
    """Concatenate two videos."""
    if not check_file_exists(filename1) or not check_file_exists(filename2):
        return

    try:
        with VideoFileClip(filename1) as video1, VideoFileClip(filename2) as video2:
            write_video(concatenate_videoclips([video1, video2]), output_filename)
    except OSError as e:
        handle_error(e)

def add_audio_to_video(video_filename: str, audio_filename: str, output_filename: str) -> None:
    """Add a WAV file to the sound of the video."""
    if not check_file_exists(video_filename) or not check_file_exists(audio_filename):
        return

    try:
        with VideoFileClip(video_filename) as video:
            write_video(video.set_audio(AudioFileClip(audio_filename)), output_filename)
    except OSError as e:
        handle_error(e)

def fade_videos(filename1: str, filename2: str, output_filename: str, duration: int = 1) -> None:
    """Fade one video into another."""
    if not check_file_exists(filename1) or not check_file_exists(filename2):
        return
    
    try:
        with VideoFileClip(filename1) as video1, VideoFileClip(filename2) as video2:
            write_video(concatenate_videoclips([video1.crossfadeout(duration), video2.crossfadein(duration)], method="compose"), output_filename)
    except OSError as e:
        handle_error(e)

def play_video(filename: str) -> None:
    """Play a video."""
    if not check_file_exists(filename):
        return

    try:
        with VideoFileClip(filename) as video:
            video.preview()
    except OSError as e:
        handle_error(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trim, concatenate, fade, play videos, or add audio to a video.")
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

    fade_parser = subparsers.add_parser("fade", help="Fade one video into another.")
    fade_parser.add_argument("filename1", help="The name of the first file to process.")
    fade_parser.add_argument("filename2", help="The name of the second file to process.")
    fade_parser.add_argument("output", help="The name of the output file.")
    fade_parser.add_argument("--duration", type=int, default=1, help="Duration of the fade effect in seconds.")

    play_parser = subparsers.add_parser("play", help="Play a video.")
    play_parser.add_argument("filename", help="The name of the file to play.")

    args = parser.parse_args()

    if args.command == "trim":
        trim_video(args.filename, args.start, args.end, args.output)
    elif args.command == "concat":
        concatenate_videos(args.filename1, args.filename2, args.output)
    elif args.command == "add_audio":
        add_audio_to_video(args.video_filename, args.audio_filename, args.output)
    elif args.command == "fade":
        fade_videos(args.filename1, args.filename2, args.output, args.duration)
    elif args.command == "play":
        play_video(args.filename)