"""
Huy Anh Nguyen
CS PhD @Stony Brook University @University of Adelaide

Created Jan 2, 2025
---------------------
After manually syncing the frames:
    - webcam2 <-> aria using audio or visual cues
    - webcam2 <-> screen using on screen UNIX timestamp or audio (less accurate)
    - And have start frame number for webcam2 -> to truncate the beginning synchronization frames.
-> Have a csv file with the following structure:
[Participant, Task, Start_Webcam2_Frame, Start_Aria_Frame, Start_Screen_Frame, End_Screen_Frame]
E.g: Dec30,P1,T1,560,560,0,-1

Screen frame sometimes is not available (corrupted file, still fixing) -> set to 0 to ignore.

The script will create a synced rgb_frames and videos folder in a similar structure to EPIC-KITCHENS:
├── P1
│   ├── T1
│   │   ├── rgb_frames
│   │   │   ├── aria
│   │   │   │   └── 00000000.jpg ...
│   │   │   ├── combined
│   │   │   │   └── 00000000.jpg ...
│   │   │   ├── webcam1
│   │   │   │   └── 00000000.jpg ...
│   │   │   └── webcam2
│   │   │       └── 00000000.jpg ...
│   │   └── videos
│   │       ├── aria.mp4
│   │       ├── combined.mp4
│   │       ├── webcam1.mp4
│   │       └── webcam2.mp4
│   ├── T2...

Usage:
python sync_vids.py --input [path_to_input_folder] --output [path_to_output_folder] --csv [csv_sync_file]
"""
import argparse
import csv
import os
import shutil

import cv2
import numpy as np

parser = argparse.ArgumentParser(description='Sync videos and frames')
parser.add_argument('-i', '--input', type=str, required=False, help='Path to the collected raw data folder')
parser.add_argument('-o', '--output', type=str, required=False, help='Path to the output folder')
parser.add_argument('-c', '--csv', type=str, required=False, help='Path to the CSV file')

args = parser.parse_args()

# for manual run or debugging
args.input = '/Volumes/SK_APFS/Touch_Dataset/New_Dataset/Raw'
args.output = '/Volumes/SK_APFS/Touch_Dataset/New_Dataset/Data'
args.csv = '/Volumes/SK_APFS/Touch_Dataset/New_Dataset/Raw/manual_sync.csv'

def create_video(out_path, frames):
    print(f'Creating video: {out_path}')
    # Create a video from a list of frame dirs
    fps = 30.0
    frame = cv2.imread(frames[0])
    frame_size = (frame.shape[1], frame.shape[0])

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(out_path, fourcc, fps, frame_size)

    for frame in frames:
        img = cv2.imread(frame)
        out.write(img)

    out.release()

    return frames

def copy_frame(out_path, frames):
    print(f'Copying frames to: {out_path}')
    for i, frame in enumerate(frames):
        destination = os.path.join(out_path, f'{i:08d}.jpg')
        shutil.copy(frame, destination)

    return frames

def create_combined_video(out_path, webcam1_frames, webcam2_frames, aria_frames, screen_frames=None):
    resolution = (2560, 1440)
    fps = 30.0
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(out_path, fourcc, fps, resolution)
    all_frames = zip(webcam1_frames, webcam2_frames, aria_frames, screen_frames) if screen_frames else zip(webcam1_frames, webcam2_frames, aria_frames)
    for frames in all_frames:
        frame = np.zeros((1440, 2560, 3), dtype=np.uint8)
        frame[:720, :1280] = cv2.resize(cv2.imread(frames[0]), (1280, 720))
        frame[:720, 1280:] = cv2.resize(cv2.imread(frames[1]), (1280, 720))
        aria = cv2.resize(cv2.imread(frames[2]), (720, 720))
        offset = (1280 - 720) // 2

        frame[720:, offset:offset+720] = aria
        if screen_frames:
            screen = cv2.resize(cv2.imread(frames[3]), (1280, 720))
            frame[720:, 1280:] = screen

        out.write(frame)

    out.release()


# Open the file
with open(args.csv, mode='r') as file:
    csv_reader = csv.reader(file)  # Create a CSV reader object

    # Iterate through the rows
    for row in csv_reader:
        base_path = os.path.join(*([args.input] + row[:3] + ['frames']))
        desc_path = os.path.join(*([args.output] + row[1:3]))
        print('-'*80)
        if os.path.exists(desc_path):
            print(f'Folder {desc_path} already exists. Skipping...')
            continue
        else:
            print(f'Processing {base_path}...')

        desc_video_path = os.path.join(desc_path, 'videos')
        desc_frame_path = os.path.join(desc_path, 'rgb_frames')

        try:
            os.makedirs(desc_video_path)
            for name in ['webcam1', 'webcam2', 'aria', 'screen']:
                os.makedirs(os.path.join(desc_frame_path, name))
        except FileExistsError:
            print(f'Folder {desc_path} already exists. Skipping...')
            continue

        all_webcam1 = [os.path.join(base_path, 'webcam1', x) for x in sorted(os.listdir(os.path.join(base_path, "webcam1")))]
        all_webcam2 = [os.path.join(base_path, 'webcam2', x) for x in sorted(os.listdir(os.path.join(base_path, "webcam2")))]
        all_aria = [os.path.join(base_path, 'aria', x) for x in sorted(os.listdir(os.path.join(base_path, "aria")))]
        all_screen = [os.path.join(base_path, 'screen', x) for x in sorted(os.listdir(os.path.join(base_path, "screen")))]

        start_webcam2, start_aria, start_screen, end_webcam2 = map(int, row[3:7])
        # Handle if there is end webcam2 screen annotation
        if end_webcam2 == 0:
            n_webcam2_frames = len(all_webcam2)
        else:
            n_webcam2_frames = min(len(all_webcam2), end_webcam2)

        print(f'Start webcam2: {start_webcam2}, End webcam2: {end_webcam2}, Start aria: {start_aria}, Start screen: {start_screen}')

        if start_screen == 0:
            # Sync frame for screen is not available.
            num_frames = min(n_webcam2_frames - start_webcam2, len(all_aria) - start_aria)
            screen_frames = None
        else:
            num_frames = min(n_webcam2_frames - start_webcam2, len(all_aria) - start_aria, len(all_screen) - start_screen)
            screen_frames = create_video(os.path.join(desc_video_path, 'screen.mp4'), all_screen[start_screen:start_screen+num_frames])
            copy_frame(os.path.join(desc_frame_path, 'screen'), screen_frames)

        print(f'Number of synced frames: {num_frames}')
        webcam1_frames = create_video(os.path.join(desc_video_path, 'webcam1.mp4'), all_webcam1[start_webcam2:start_webcam2+num_frames])
        copy_frame(os.path.join(desc_frame_path, 'webcam1'), webcam1_frames)

        webcam2_frames = create_video(os.path.join(desc_video_path, 'webcam2.mp4'), all_webcam2[start_webcam2:start_webcam2+num_frames])
        copy_frame(os.path.join(desc_frame_path, 'webcam2'), webcam2_frames)

        aria_frames = create_video(os.path.join(desc_video_path, 'aria.mp4'), all_aria[start_aria:start_aria+num_frames])
        copy_frame(os.path.join(desc_frame_path, 'aria'), aria_frames)

        # Create combined video
        create_combined_video(os.path.join(desc_video_path, 'combined.mp4'), webcam1_frames, webcam2_frames, aria_frames, screen_frames)
