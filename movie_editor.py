import os
import subprocess
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

def run_ffmpeg_command(command: str) -> None:
    """Run an ffmpeg command."""
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        handle_error(e)

def trim_video(filename: str, start_time: str, end_time: str, output_filename: str) -> None:
    """Trim a video from start time to end time."""
    if not check_file_exists(filename):
        return
    
    start_time_sec, end_time_sec = time_to_seconds(start_time), time_to_seconds(end_time)
    command = f"ffmpeg -i {filename} -ss {start_time_sec} -to {end_time_sec} -c copy {output_filename}"
    run_ffmpeg_command(command)
    print(f"Video trimmed and saved as {output_filename}")

def concatenate_videos(filename1: str, filename2: str, output_filename: str) -> None:
    """Concatenate two videos."""
    if not check_file_exists(filename1) or not check_file_exists(filename2):
        return
    
    with open("videos.txt", "w") as f:
        f.write(f"file '{filename1}'\n")
        f.write(f"file '{filename2}'\n")
    
    command = f"ffmpeg -f concat -safe 0 -i videos.txt -c copy {output_filename}"
    run_ffmpeg_command(command)
    os.remove("videos.txt")
    print(f"Videos concatenated and saved as {output_filename}")

def concatenate_videos_in_folder(folder: str, output_filename: str) -> None:
    """Concatenate all videos in a folder using ffmpeg."""
    if not os.path.isdir(folder):
        print(f"Error: The folder {folder} does not exist.")
        return
    
    video_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(('.mp4', '.avi', '.mov'))]
    if not video_files:
        print(f"No video files found in the folder {folder}.")
        return

    with open("videos.txt", "w") as f:
        for video_file in video_files:
            f.write(f"file '{video_file}'\n")
    
    command = f"ffmpeg -f concat -safe 0 -i videos.txt -c copy {output_filename}"
    run_ffmpeg_command(command)
    os.remove("videos.txt")
    print(f"Videos concatenated and saved as {output_filename}")

def add_audio_to_video(video_filename: str, audio_filename: str, output_filename: str) -> None:
    """Add a WAV file to the sound of the video."""
    if not check_file_exists(video_filename) or not check_file_exists(audio_filename):
        return

    command = f"ffmpeg -i {video_filename} -i {audio_filename} -c:v copy -c:a aac {output_filename}"
    run_ffmpeg_command(command)
    print(f"Audio added and video saved as {output_filename}")

def fade_videos(filename1: str, filename2: str, output_filename: str, duration: int = 1) -> None:
    """Fade one video into another."""
    if not check_file_exists(filename1) or not check_file_exists(filename2):
        return
    
    temp_output1 = "temp_output1.mp4"
    temp_output2 = "temp_output2.mp4"
    
    command1 = f"ffmpeg -i {filename1} -vf 'fade=t=out:st=0:d={duration}' {temp_output1}"
    command2 = f"ffmpeg -i {filename2} -vf 'fade=t=in:st=0:d={duration}' {temp_output2}"
    
    run_ffmpeg_command(command1)
    run_ffmpeg_command(command2)
    
    concatenate_videos(temp_output1, temp_output2, output_filename)
    
    os.remove(temp_output1)
    os.remove(temp_output2)
    print(f"Videos faded and saved as {output_filename}")

def play_video(filename: str) -> None:
    """Play a video."""
    if not check_file_exists(filename):
        return
        
    command = f"ffplay {filename}"
    run_ffmpeg_command(command)

def play_all_videos_in_folder(folder: str) -> None:
    """Play all videos in a folder."""
    if not os.path.isdir(folder):
        print(f"Error: The folder {folder} does not exist.")
        return

    video_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(('.mp4', '.avi', '.mov'))]
    if not video_files:
        print(f"No video files found in the folder {folder}.")
        return

    for video_file in video_files:
        print(f"Playing {video_file}...")
        play_video(video_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trim, concatenate, fade, play videos, or add audio to a video.")
    subparsers = parser.add_subparsers(dest="command")

    trim_parser = subparsers.add_parser("trim", help="Trim a video from start time to end time.")
    trim_parser.add_argument("-f", "--filename", help="The name of the file to process.", required=True)
    trim_parser.add_argument("-s", "--start", help="The start time in HH:MM:SS or MM:SS format.", required=True)
    trim_parser.add_argument("-e", "--end", help="The end time in HH:MM:SS or MM:SS format.", required=True)
    trim_parser.add_argument("-o", "--output", help="The name of the output file.", required=True)

    concat_parser = subparsers.add_parser("concat", help="Concatenate two videos.")
    concat_parser.add_argument("-f1", "--filename1", help="The name of the first file to process.", required=True)
    concat_parser.add_argument("-f2", "--filename2", help="The name of the second file to process.", required=True)
    concat_parser.add_argument("-o", "--output", help="The name of the output file.", required=True)

    audio_parser = subparsers.add_parser("add_audio", help="Add a WAV file to the sound of the video.")
    audio_parser.add_argument("-v", "--video_filename", help="The name of the video file to process.", required=True)
    audio_parser.add_argument("-a", "--audio_filename", help="The name of the audio file to add.", required=True)
    audio_parser.add_argument("-o", "--output", help="The name of the output file.", required=True)

    fade_parser = subparsers.add_parser("fade", help="Fade one video into another.")
    fade_parser.add_argument("-f1", "--filename1", help="The name of the first file to process.", required=True)
    fade_parser.add_argument("-f2", "--filename2", help="The name of the second file to process.", required=True)
    fade_parser.add_argument("-o", "--output", help="The name of the output file.", required=True)
    fade_parser.add_argument("-d", "--duration", type=int, default=1, help="Duration of the fade effect in seconds.")

    play_parser = subparsers.add_parser("play", help="Play a video.")
    play_parser.add_argument("-f", "--filename", help="The name of the file to play.", required=True)

    play_all_parser = subparsers.add_parser("play_all_videos_in_folder", help="Play all videos in a folder.")
    play_all_parser.add_argument("-d", "--folder", help="The name of the folder to process.", required=True)

    concat_folder_parser = subparsers.add_parser("concatenate_videos_in_folder", help="Concatenate all videos in a folder.")
    concat_folder_parser.add_argument("-d", "--folder", help="The name of the folder to process.", required=True)
    concat_folder_parser.add_argument("-o", "--output", help="The name of the output file.", required=True)

    args = parser.parse_args()

    # Ensure ffmpeg is installed
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print("Error: ffmpeg is not installed. Please install ffmpeg to use this script.")
        exit(1)

    if args.command in ["trim", "t"]:
        trim_video(args.filename, args.start, args.end, args.output)
    elif args.command in ["concat", "c"]:
        concatenate_videos(args.filename1, args.filename2, args.output)
    elif args.command in ["add_audio", "aa"]:
        add_audio_to_video(args.video_filename, args.audio_filename, args.output)
    elif args.command in ["fade", "f"]:
        fade_videos(args.filename1, args.filename2, args.output, args.duration)
    elif args.command in ["play", "p"]:
        play_video(args.filename)
    elif args.command in ["play_all_videos_in_folder", "paf"]:
        play_all_videos_in_folder(args.folder)
    elif args.command in ["concatenate_videos_in_folder", "cvf"]:
        concatenate_videos_in_folder(args.folder, args.output)
