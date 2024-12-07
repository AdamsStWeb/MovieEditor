package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
)

func timeToSeconds(timeStr string) (int, error) {
	fmt.Printf("Converting time string %s to seconds\n", timeStr)
	parts := strings.Split(timeStr, ":")
	if len(parts) < 2 || len(parts) > 3 {
		return 0, fmt.Errorf("invalid time format. Use HH:MM:SS or MM:SS")
	}

	var h, m, s int
	var err error

	if len(parts) == 3 {
		h, err = strconv.Atoi(parts[0])
		if err != nil {
			return 0, err
		}
		m, err = strconv.Atoi(parts[1])
		if err != nil {
			return 0, err
		}
		s, err = strconv.Atoi(parts[2])
		if err != nil {
			return 0, err
		}
	} else {
		m, err = strconv.Atoi(parts[0])
		if err != nil {
			return 0, err
		}
		s, err = strconv.Atoi(parts[1])
		if err != nil {
			return 0, err
		}
	}

	seconds := h*3600 + m*60 + s
	fmt.Printf("Converted time string %s to %d seconds\n", timeStr, seconds)
	return seconds, nil
}

func checkFileExists(filename string) bool {
	fmt.Printf("Checking if file %s exists\n", filename)
	if _, err := os.Stat(filename); os.IsNotExist(err) {
		fmt.Printf("Error: The file %s does not exist.\n", filename)
		return false
	}
	fmt.Printf("File %s exists\n", filename)
	return true
}

func handleError(err error) {
	fmt.Printf("Error: %v\n", err)
	fmt.Println("Files in the current directory:")
	files, _ := os.ReadDir(".")
	for _, file := range files {
		fmt.Println(file.Name())
	}
}

func runFFmpegCommand(command string) {
	fmt.Printf("Running command: %s\n", command)
	cmd := exec.Command("sh", "-c", command)
	err := cmd.Run()
	if err != nil {
		handleError(err)
	}
}

func createFileList(filenames []string) (string, error) {
	file, err := os.Create("videos.txt")
	if err != nil {
		return "", err
	}
	defer file.Close()

	for _, filename := range filenames {
		file.WriteString(fmt.Sprintf("file '%s'\n", filename))
	}

	return "videos.txt", nil
}

func trimVideo(filename, startTime, endTime, outputFilename string) {
	fmt.Printf("Trimming video %s from %s to %s, outputting to %s\n", filename, startTime, endTime, outputFilename)
	if !checkFileExists(filename) {
		return
	}

	startTimeSec, err := timeToSeconds(startTime)
	if err != nil {
		handleError(err)
		return
	}
	endTimeSec, err := timeToSeconds(endTime)
	if err != nil {
		handleError(err)
		return
	}

	command := fmt.Sprintf("ffmpeg -i %s -ss %d -to %d -c copy %s", filename, startTimeSec, endTimeSec, outputFilename)
	runFFmpegCommand(command)
	fmt.Printf("Video trimmed and saved as %s\n", outputFilename)
}

func concatenateVideos(filenames []string, outputFilename string) {
	fmt.Printf("Concatenating videos %v, outputting to %s\n", filenames, outputFilename)
	for _, filename := range filenames {
		if !checkFileExists(filename) {
			return
		}
	}

	fileList, err := createFileList(filenames)
	if err != nil {
		handleError(err)
		return
	}
	defer os.Remove(fileList)

	command := fmt.Sprintf("ffmpeg -f concat -safe 0 -i %s -c copy %s", fileList, outputFilename)
	runFFmpegCommand(command)
	fmt.Printf("Videos concatenated and saved as %s\n", outputFilename)
}

func concatenateVideosInFolder(folder, outputFilename string) {
	fmt.Printf("Concatenating all videos in folder %s, outputting to %s\n", folder, outputFilename)
	if _, err := os.Stat(folder); os.IsNotExist(err) {
		fmt.Printf("Error: The folder %s does not exist.\n", folder)
		return
	}

	files, err := os.ReadDir(folder)
	if err != nil {
		handleError(err)
		return
	}

	var videoFiles []string
	for _, file := range files {
		if strings.HasSuffix(file.Name(), ".mp4") || strings.HasSuffix(file.Name(), ".avi") || strings.HasSuffix(file.Name(), ".mov") {
			videoFiles = append(videoFiles, filepath.Join(folder, file.Name()))
		}
	}

	if len(videoFiles) == 0 {
		fmt.Printf("No video files found in the folder %s.\n", folder)
		return
	}

	concatenateVideos(videoFiles, outputFilename)
}

func addAudioToVideo(videoFilename, audioFilename, outputFilename string) {
	fmt.Printf("Adding audio %s to video %s, outputting to %s\n", audioFilename, videoFilename, outputFilename)
	if !checkFileExists(videoFilename) || !checkFileExists(audioFilename) {
		return
	}

	command := fmt.Sprintf("ffmpeg -i %s -i %s -c:v copy -c:a aac %s", videoFilename, audioFilename, outputFilename)
	runFFmpegCommand(command)
	fmt.Printf("Audio added and video saved as %s\n", outputFilename)
}

func fadeVideos(filename1, filename2, outputFilename string, duration int) {
	fmt.Printf("Fading videos %s and %s with duration %d, outputting to %s\n", filename1, filename2, duration, outputFilename)
	if !checkFileExists(filename1) || !checkFileExists(filename2) {
		return
	}

	tempOutput1 := "temp_output1.mp4"
	tempOutput2 := "temp_output2.mp4"

	command1 := fmt.Sprintf("ffmpeg -i %s -vf 'fade=t=out:st=0:d=%d' %s", filename1, duration, tempOutput1)
	command2 := fmt.Sprintf("ffmpeg -i %s -vf 'fade=t=in:st=0:d=%d' %s", filename2, duration, tempOutput2)

	runFFmpegCommand(command1)
	runFFmpegCommand(command2)

	concatenateVideos([]string{tempOutput1, tempOutput2}, outputFilename)

	os.Remove(tempOutput1)
	os.Remove(tempOutput2)
	fmt.Printf("Videos faded and saved as %s\n", outputFilename)
}

func playVideo(filename string) {
	fmt.Printf("Playing video %s\n", filename)
	if !checkFileExists(filename) {
		return
	}

	command := fmt.Sprintf("ffplay %s", filename)
	runFFmpegCommand(command)
}

func playAllVideosInFolder(folder string) {
	fmt.Printf("Playing all videos in folder %s\n", folder)
	if _, err := os.Stat(folder); os.IsNotExist(err) {
		fmt.Printf("Error: The folder %s does not exist.\n", folder)
		return
	}

	files, err := os.ReadDir(folder)
	if err != nil {
		handleError(err)
		return
	}

	var videoFiles []string
	for _, file := range files {
		if strings.HasSuffix(file.Name(), ".mp4") || strings.HasSuffix(file.Name(), ".avi") || strings.HasSuffix(file.Name(), ".mov") {
			videoFiles = append(videoFiles, filepath.Join(folder, file.Name()))
		}
	}

	if len(videoFiles) == 0 {
		fmt.Printf("No video files found in the folder %s.\n", folder)
		return
	}

	for _, videoFile := range videoFiles {
		fmt.Printf("Playing %s...\n", videoFile)
		playVideo(videoFile)
	}
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: go run movieEditor.go <command> [<args>]")
		return
	}

	command := os.Args[1]
	fmt.Printf("Executing command: %s\n", command)

	switch command {
	case "trim", "-t", "trim_video", "--trim":
		// Example: go run movieEditor.go trim input.mp4 00:00:10 00:00:20 output.mp4
		if len(os.Args) != 6 {
			fmt.Println("Usage: go run movieEditor.go trim <filename> <start> <end> <output>")
			return
		}
		trimVideo(os.Args[2], os.Args[3], os.Args[4], os.Args[5])
	case "concat", "-c", "concatenate", "--concat", "c":
		// Example: go run movieEditor.go concat input1.mp4 input2.mp4 output.mp4
		if len(os.Args) != 5 {
			fmt.Println("Usage: go run movieEditor.go concat <filename1> <filename2> <output>")
			return
		}
		concatenateVideos([]string{os.Args[2], os.Args[3]}, os.Args[4])
	case "concat_folder", "-cf", "concat_folder_videos", "--concat_folder", "cf":
		// Example: go run movieEditor.go concat_folder videos_folder output.mp4
		if len(os.Args) != 4 {
			fmt.Println("Usage: go run movieEditor.go concat_folder <folder> <output>")
			return
		}
		concatenateVideosInFolder(os.Args[2], os.Args[3])
	case "add_audio", "-a", "add_audio_to_video", "--add_audio":
		// Example: go run movieEditor.go add_audio input.mp4 audio.mp3 output.mp4
		if len(os.Args) != 5 {
			fmt.Println("Usage: go run movieEditor.go add_audio <video_filename> <audio_filename> <output>")
			return
		}
		addAudioToVideo(os.Args[2], os.Args[3], os.Args[4])
	case "fade", "-f", "fade_videos", "--fade":
		// Example: go run movieEditor.go fade input1.mp4 input2.mp4 output.mp4 5
		if len(os.Args) != 6 {
			fmt.Println("Usage: go run movieEditor.go fade <filename1> <filename2> <output> <duration>")
			return
		}
		duration, err := strconv.Atoi(os.Args[5])
		if err != nil {
			handleError(err)
			return
		}
		fadeVideos(os.Args[2], os.Args[3], os.Args[4], duration)
	case "play", "-p", "play_video", "--play", "p":
		// Example: go run movieEditor.go play input.mp4
		if len(os.Args) != 3 {
			fmt.Println("Usage: go run movieEditor.go play <filename>")
			return
		}
		playVideo(os.Args[2])
	case "play_all", "-pa", "play_all_videos", "--play_all":
		// Example: go run movieEditor.go play_all videos_folder
		if len(os.Args) != 3 {
			fmt.Println("Usage: go run movieEditor.go play_all <folder>")
			return
		}
		playAllVideosInFolder(os.Args[2])
	default:
		fmt.Println("Usage: go run movieEditor.go <command> [<args>]")
		fmt.Println("Commands:")
		fmt.Println("  trim, -t, trim_video, --trim <filename> <start> <end> <output> - Trim a video")
		fmt.Println("  concat, -c, concatenate, --concat <filename1> <filename2> <output> - Concatenate two videos")
		fmt.Println("  concat_folder, -cf, concat_folder_videos, --concat_folder <folder> <output> - Concatenate all videos in a folder")
		fmt.Println("  add_audio, -a, add_audio_to_video, --add_audio <video_filename> <audio_filename> <output> - Add audio to a video")
		fmt.Println("  fade, -f, fade_videos, --fade <filename1> <filename2> <output> <duration> - Fade between two videos")
		fmt.Println("  play, -p, play_video, --play <filename> - Play a video")
		fmt.Println("  play_all, -pa, play_all_videos, --play_all <folder> - Play all videos in a folder")
	}
}
