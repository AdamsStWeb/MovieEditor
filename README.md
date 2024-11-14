# Movie Editor

This script provides various functionalities for video editing using the `moviepy` library. You can trim, concatenate, fade, play videos, or add audio to a video.

## Requirements

- Python 3.x
- moviepy
- argparse

You can install the required libraries using pip:

```sh
pip install moviepy
```

## Usage

The script supports several commands. Below are the available commands and their usage:

### Trim a Video

Trim a video from start time to end time.

```sh
python movie_editor.py trim <filename> <start_time> <end_time> <output_filename>
```

### Concatenate Two Videos

Concatenate two videos into one.

```sh
python movie_editor.py concat <filename1> <filename2> <output_filename>
```

### Add Audio to a Video

Add a WAV file to the sound of the video.

```sh
python movie_editor.py add_audio <video_filename> <audio_filename> <output_filename>
```

### Fade One Video into Another

Fade one video into another with a specified duration.

```sh
python movie_editor.py fade <filename1> <filename2> <output_filename> [--duration <seconds>]
```

### Play a Video

Play a video file.

```sh
python movie_editor.py play <filename>
```

## Functions

- `time_to_seconds(time_str: str) -> int`: Convert time string in HH:MM:SS or MM:SS format to seconds.
- `check_file_exists(filename: str) -> bool`: Check if a file exists.
- `handle_error(e: Exception) -> None`: Handle errors by printing the error message and listing files in the current directory.
- `write_video(video, output_filename: str) -> None`: Write the video to a file.
- `process_video_files(filenames: list, output_filename: str, process_func) -> None`: Process video files with a given function.
- `trim_video(filename: str, start_time: str, end_time: str, output_filename: str) -> None`: Trim a video from start time to end time.
- `concatenate_videos(filename1: str, filename2: str, output_filename: str) -> None`: Concatenate two videos.
- `add_audio_to_video(video_filename: str, audio_filename: str, output_filename: str) -> None`: Add a WAV file to the sound of the video.
- `fade_videos(filename1: str, filename2: str, output_filename: str, duration: int = 1) -> None`: Fade one video into another.
- `play_video(filename: str) -> None`: Play a video.

## License

This project is licensed under the MIT License.