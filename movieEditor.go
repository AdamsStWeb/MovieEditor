package main

import (
	"flag"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
)

func timeToSeconds(timeStr string) (int, error) {
	parts := strings.Split(timeStr, ":")
	if len(parts) == 2 {
		minutes, err := strconv.Atoi(parts[0])
		if err != nil {
			return 0, err
		}
		seconds, err := strconv.Atoi(parts[1])
		if err != nil {
			return 0, err
		}
		return minutes*60 + seconds, nil
	} else if len(parts) == 3 {
		hours, err := strconv.Atoi(parts[0])
		if err != nil {
			return 0, err
		}
		minutes, err := strconv.Atoi(parts[1])
		if err != nil {
			return 0, err
		}
		seconds, err := strconv.Atoi(parts[2])
		if err != nil {
			return 0, err
		}
		return hours*3600 + minutes*60 + seconds, nil
	} else {
		return 0, fmt.Errorf("invalid time format. Use HH:MM:SS or MM:SS")
	}
}

func runFFmpeg(args ...string) error {
	cmd := exec.Command("ffmpeg", args...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	return cmd.Run()
}

func trimVideo(filename, startTimeStr, endTimeStr, outputFilename string) error {
	if _, err := os.Stat(filename); os.IsNotExist(err) {
		return fmt.Errorf("the file %s does not exist", filename)
	}

	startTime, err := timeToSeconds(startTimeStr)
	if err != nil {
		return err
	}
	endTime, err := timeToSeconds(endTimeStr)
	if err != nil {
		return err
	}

	startTimeStr = fmt.Sprintf("%02d:%02d:%02d", startTime/3600, (startTime%3600)/60, startTime%60)
	endTimeStr = fmt.Sprintf("%02d:%02d:%02d", endTime/3600, (endTime%3600)/60, endTime%60)

	return runFFmpeg("-i", filename, "-ss", startTimeStr, "-to", endTimeStr, "-c", "copy", outputFilename)
}

func concatenateVideos(filename1, filename2, outputFilename string) error {
	if _, err := os.Stat(filename1); os.IsNotExist(err) {
		return fmt.Errorf("the file %s does not exist", filename1)
	}
	if _, err := os.Stat(filename2); os.IsNotExist(err) {
		return fmt.Errorf("the file %s does not exist", filename2)
	}

	listFile := "concat_list.txt"
	listContent := fmt.Sprintf("file '%s'\nfile '%s'\n", filename1, filename2)
	err := os.WriteFile(listFile, []byte(listContent), 0644)
	if err != nil {
		return err
	}
	defer os.Remove(listFile)

	return runFFmpeg("-f", "concat", "-safe", "0", "-i", listFile, "-c", "copy", outputFilename)
}

func addAudioToVideo(videoFilename, audioFilename, outputFilename string) error {
	if _, err := os.Stat(videoFilename); os.IsNotExist(err) {
		return fmt.Errorf("the file %s does not exist", videoFilename)
	}
	if _, err := os.Stat(audioFilename); os.IsNotExist(err) {
		return fmt.Errorf("the file %s does not exist", audioFilename)
	}

	return runFFmpeg("-i", videoFilename, "-i", audioFilename, "-c:v", "copy", "-c:a", "aac", "-strict", "experimental", outputFilename)
}

func splitVideo(filename, splitDurationStr string) error {
	if _, err := os.Stat(filename); os.IsNotExist(err) {
		return fmt.Errorf("the file %s does not exist", filename)
	}

	splitDuration, err := timeToSeconds(splitDurationStr)
	if err != nil {
		return err
	}

	videoDurationCmd := exec.Command("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filename)
	output, err := videoDurationCmd.Output()
	if err != nil {
		return err
	}

	videoDuration, err := strconv.ParseFloat(strings.TrimSpace(string(output)), 64)
	if err != nil {
		return err
	}

	for startTime := 0; startTime < int(videoDuration); startTime += splitDuration {
		endTime := startTime + splitDuration
		if endTime > int(videoDuration) {
			endTime = int(videoDuration)
		}
		outputFilename := fmt.Sprintf("%s_part%d.mp4", strings.TrimSuffix(filename, filepath.Ext(filename)), startTime/splitDuration+1)
		startTimeStr := fmt.Sprintf("%02d:%02d:%02d", startTime/3600, (startTime%3600)/60, startTime%60)
		endTimeStr := fmt.Sprintf("%02d:%02d:%02d", endTime/3600, (endTime%3600)/60, endTime%60)
		err := runFFmpeg("-i", filename, "-ss", startTimeStr, "-to", endTimeStr, "-c", "copy", outputFilename)
		if err != nil {
			return err
		}
		fmt.Printf("Created %s\n", outputFilename)
	}

	return nil
}

func main() {
	trimCmd := flag.NewFlagSet("trim", flag.ExitOnError)
	trimFilename := trimCmd.String("filename", "", "The name of the file to process")
	trimStart := trimCmd.String("start", "", "The start time in HH:MM:SS or MM:SS format")
	trimEnd := trimCmd.String("end", "", "The end time in HH:MM:SS or MM:SS format")
	trimOutput := trimCmd.String("output", "", "The name of the output file")

	concatCmd := flag.NewFlagSet("concat", flag.ExitOnError)
	concatFilename1 := concatCmd.String("filename1", "", "The name of the first file to process")
	concatFilename2 := concatCmd.String("filename2", "", "The name of the second file to process")
	concatOutput := concatCmd.String("output", "", "The name of the output file")

	addAudioCmd := flag.NewFlagSet("add_audio", flag.ExitOnError)
	addAudioVideoFilename := addAudioCmd.String("video_filename", "", "The name of the video file to process")
	addAudioAudioFilename := addAudioCmd.String("audio_filename", "", "The name of the audio file to add")
	addAudioOutput := addAudioCmd.String("output", "", "The name of the output file")

	splitCmd := flag.NewFlagSet("split", flag.ExitOnError)
	splitFilename := splitCmd.String("filename", "", "The name of the file to process")
	splitDuration := splitCmd.String("duration", "", "The duration of each split part in HH:MM:SS or MM:SS format")

	if len(os.Args) < 2 {
		fmt.Println("expected 'trim', 'concat', 'add_audio', or 'split' subcommands")
		os.Exit(1)
	}

	switch os.Args[1] {
	case "trim":
		trimCmd.Parse(os.Args[2:])
		if *trimFilename == "" || *trimStart == "" || *trimEnd == "" || *trimOutput == "" {
			trimCmd.Usage()
			os.Exit(1)
		}
		err := trimVideo(*trimFilename, *trimStart, *trimEnd, *trimOutput)
		if err != nil {
			fmt.Println("Error:", err)
		}
	case "concat":
		concatCmd.Parse(os.Args[2:])
		if *concatFilename1 == "" || *concatFilename2 == "" || *concatOutput == "" {
			concatCmd.Usage()
			os.Exit(1)
		}
		err := concatenateVideos(*concatFilename1, *concatFilename2, *concatOutput)
		if err != nil {
			fmt.Println("Error:", err)
		}
	case "add_audio":
		addAudioCmd.Parse(os.Args[2:])
		if *addAudioVideoFilename == "" || *addAudioAudioFilename == "" || *addAudioOutput == "" {
			addAudioCmd.Usage()
			os.Exit(1)
		}
		err := addAudioToVideo(*addAudioVideoFilename, *addAudioAudioFilename, *addAudioOutput)
		if err != nil {
			fmt.Println("Error:", err)
		}
	case "split":
		splitCmd.Parse(os.Args[2:])
		if *splitFilename == "" || *splitDuration == "" {
			splitCmd.Usage()
			os.Exit(1)
		}
		err := splitVideo(*splitFilename, *splitDuration)
		if err != nil {
			fmt.Println("Error:", err)
		}
	default:
		fmt.Println("expected 'trim', 'concat', 'add_audio', or 'split' subcommands")
		os.Exit(1)
	}
}
