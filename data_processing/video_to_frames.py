"""
Huy Anh Nguyen
CS PhD @Stony Brook University @University of Adelaide

Created Jan 2, 2025
---------------------
Convert multiple streams video from OBS to 3 separate folders of frames.
Top left: (1920, 1080) -> Side webcam (webcam1)
Top right: (1920, 1080) -> Top webcam (webcam2)
Bottom left: (1920, 1080) -> Screen capture (screen).

Expect input folder structure similar to EPIC-KITCHENS:
Dec30
├── P1
│   ├── T1
│   │   ├── aria.vrs
│   │   ├── aria.vrs.json
│   │   ├── aria.mp4        <- converted from aria.vrs using vrs_to_mp4
│   │   ├── screen.png      <- from Repaper Studio
│   │   └── obs.mp4         <- from OBS
│   ├── T2 ...

Usage:
python video_to_frames.py -i [path_to_data_folder]
"""

import argparse
import os
from glob import glob

import cv2

parser = argparse.ArgumentParser(description='Convert multiple streams video from OBS to 3 separate folders of frames.')
parser.add_argument('-i', '--input', type=str, help='Path to the collected data folder')
parser.add_argument('-v', '--video', type=str, help='Path to a single video file')
args = parser.parse_args()

# args.input = 'SOMETIME' # for manual run

def main(vid):
    print(f'Processing {vid}')
    dir_path = os.path.join(os.path.dirname(vid), 'frames')
    os.makedirs(os.path.join(dir_path, 'webcam1'), exist_ok=True)
    webcam1_dir = os.path.join(dir_path, 'webcam1')
    webcam2_dir = os.path.join(dir_path, 'webcam2')
    screen_dir = os.path.join(dir_path, 'screen')
    aria_dir = os.path.join(dir_path, 'aria')

    os.makedirs(webcam1_dir, exist_ok=True)
    os.makedirs(webcam2_dir, exist_ok=True)
    os.makedirs(screen_dir, exist_ok=True)
    os.makedirs(aria_dir, exist_ok=True)

    # Read video
    cap = cv2.VideoCapture(vid)
    frame_count = 0
    max_frames = 1e6 # modify this to limit the number of frames to be extracted for syncing purpose

    # Read frames one by one
    while frame_count < max_frames:
        ret, frame = cap.read()  # ret: success flag, frame: the frame data
        if not ret:
            print(f"Extracted {frame_count} frames")
            break

        if 'aria.mp4' in vid:
            cv2.imwrite(os.path.join(aria_dir, f'{frame_count:08d}.jpg'), frame)
        else:
            cv2.imwrite(os.path.join(webcam1_dir, f'{frame_count:08d}.jpg'), frame[:1080, :1920, :])
            cv2.imwrite(os.path.join(webcam2_dir, f'{frame_count:08d}.jpg'), frame[:1080, 1920:, :])
            cv2.imwrite(os.path.join(screen_dir, f'{frame_count:08d}.jpg'), frame[1080:, :1920, :])

        frame_count += 1

if args.video:
    main(args.video)
elif args.input:
    all_videos = sorted(glob(os.path.join(args.input, '*', '*', '*.mp4')))
    for vid in all_videos:
        main(vid)
else:
    print('Please provide either --input or --video argument')

