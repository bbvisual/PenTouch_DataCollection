"""
Huy Anh Nguyen
CS PhD @Stony Brook University @University of Adelaide

Created Jan 2, 2025
---------------------
When pen touches the repaper, the Repaper Studio crosshair will turn magenta. This script will automatically annotate the touch frames
The magneta crosshair is unique so no need to select the region of interest.
"""


import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Annotate touch frames based on green LED detection')
parser.add_argument('-i', '--input', type=str, required=True, help='Path to the collected data folder')
# parser.add_argument('-i', '--input', type=str, default='/Volumes/SK_APFS/Touch_Dataset/New_Dataset/Raw/Data')
parser.add_argument('-d', '--debug', action='store_true', help='Debug mode, will create a manual verification folder')

args = parser.parse_args()
args.input = Path(args.input)

lower, upper = np.array([150, 100, 100]), np.array([165, 255, 255])

# Main loop to process all splits
all_videos = sorted(list(args.input.glob('*/*/rgb_frames/screen')))
print(f'[INFO] Total {len(all_videos)} videos...')

for vid in sorted(all_videos):
    if '.DS_Store' in str(vid): # annoying macOS
        continue

    """Main function to process frames and select regions of interest."""
    # anno_path = os.path.join(args.input, vid, 'annotation.json')
    anno_path = vid.parents[1].joinpath('screen_touch_annotation.json')
    all_frames = sorted(vid.glob('*.jpg'))

    if anno_path.exists():
        print(f"[INFO] {anno_path} already exists. Skip this video.")
        continue

    print('=' * 80)
    print(f"[INFO] Processing {Path(*vid.parts[-4:])} ...")

    res = {'bbox': None, 'annotations': {}}
    if len(all_frames) == 0:
            print("No screen frames found. Skip this video.")
            continue

    if args.debug:
        # Create a temporary separation folder to manually verify the touch annotation
        print(f"[INFO] Debug mode. Creating manual verification folder ...")
        pos_dir = vid.parents[1].joinpath('screen_manual_verification', 'touch')
        pos_dir.mkdir(parents=True, exist_ok=True)

        neg_dir = vid.parents[1].joinpath('screen_manual_verification', 'non_touch')
        neg_dir.mkdir(parents=True, exist_ok=True)

    # Detect touch or non-touch based on the green LED in the average bounding box
    pos_cnt = 0
    neg_cnt = 0
    for frame_path in tqdm(all_frames):
        img = cv2.imread(frame_path)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)

        if np.count_nonzero(mask) > 0:
            res['annotations'][frame_path.name] = 1
            pos_cnt += 1
            if args.debug:
                cv2.imwrite(pos_dir.joinpath(frame_path.name), img)
                cv2.imwrite(pos_dir.joinpath(frame_path.name.replace('.jpg', '_mask.jpg')), mask)

        else:
            res['annotations'][frame_path.name] = 0
            neg_cnt += 1
            if args.debug:
                cv2.imwrite(neg_dir.joinpath(frame_path.name), img)

    print(f'{vid} done. Touch: {pos_cnt} Non-touch: {neg_cnt}')

    with open(anno_path, 'w') as f:
        json.dump(res, f, indent=4)
