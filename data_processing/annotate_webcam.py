"""
Huy Anh Nguyen
CS PhD @Stony Brook University @University of Adelaide

Created Jan 2, 2025
---------------------
When pen touches the repaper, a green LED will light up. This script will automatically annotate the touch frames
based on the green LED detection in HSV color space.
To make it more accurate, the script will ask for the region of interest to detect the green LED.
For each video, 3 frames will be randomly selected for bounding box selection. Then merged bounding box will be used
to detect touch frames.

Note: the script only search for webcam2 streams as aria glasses and webcam1 green color is not that accurate.
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
parser.add_argument('-s', '--stream', type=str, default='webcam2', help='Stream to process (webcam1, webcam2, aria)')
parser.add_argument('-d', '--debug', action='store_true', help='Debug mode, will create a manual verification folder')

args = parser.parse_args()

args.input = Path(args.input)

COLOR_BOUND = {'webcam1': [None,
                           None],
               'webcam2': [[45, 50, 100],
                           [90, 255, 255]],
               'aria': [None,
                        None]
               }

lower_green, upper_green = list(map(np.array, COLOR_BOUND[args.stream]))

# Mouse callback function to draw the bounding box
def draw_bbox(event, x, y, flags, param):
    start_point, end_point, drawing, img = param

    # Start drawing the rectangle (on left mouse button down)
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing[0] = True
        start_point[0], start_point[1] = x, y

    # Update the rectangle (on mouse move)
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing[0]:
            end_point[0], end_point[1] = x, y

    # Finish drawing the rectangle (on left mouse button up)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing[0] = False
        end_point[0], end_point[1] = x, y

def select_roi(image_path):
    """Open an image and allow the user to draw a bounding box. Return the coordinates."""
    # Load the image
    img = cv2.imread(image_path)
    temp_img = img.copy()

    # Initialize variables for start/end points and drawing state
    start_point = [0, 0]
    end_point = [0, 0]
    drawing = [False]

    # Create a window and set the mouse callback
    cv2.namedWindow("Select ROI")
    cv2.setMouseCallback("Select ROI", draw_bbox, [start_point, end_point, drawing, img])

    while True:
        # Draw the rectangle while dragging the mouse
        if drawing[0]:
            temp_img = img.copy()
            cv2.rectangle(temp_img, tuple(start_point), tuple(end_point), (0, 255, 0), 2)

        # Show the image
        cv2.imshow("Select ROI", temp_img)

        # Break the loop on 'q' or Enter key press
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 13:
            break

    cv2.destroyAllWindows()

    # Return the bounding box coordinates if available
    if start_point != end_point:
        return start_point[0], start_point[1], end_point[0], end_point[1]
    else:
        return None

def union_bboxes(bboxes):
    """Calculate the union of all bounding boxes."""
    x1_union = min([bbox[0] for bbox in bboxes])  # Smallest x1
    y1_union = min([bbox[1] for bbox in bboxes])  # Smallest y1
    x2_union = max([bbox[2] for bbox in bboxes])  # Largest x2
    y2_union = max([bbox[3] for bbox in bboxes])  # Largest y2
    return (x1_union, y1_union, x2_union, y2_union)

# Main loop to process all splits
all_videos = sorted(list(args.input.glob(f'*/*/rgb_frames/{args.stream}')))
print(f'[INFO] Total {len(all_videos)} videos...')

for vid in sorted(all_videos):
    if '.DS_Store' in str(vid): # annoying macOS
        continue

    """Main function to process frames and select regions of interest."""
    anno_path = vid.parents[1].joinpath(f'{args.stream}_touch_annotation.json')
    all_frames = sorted(vid.glob('*.jpg'))

    if anno_path.exists():
        print(f"[INFO] {anno_path} already exists. Skip this video.")
        continue

    print('=' * 80)
    print(f"[INFO] Processing {Path(*vid.parts[-4:])} ...")

    res = {'bbox': None, 'annotations': {}}
    if len(all_frames) < 3:
            print("Not enough frames to select from.")
            continue

    if args.debug:
        # Create a temporary separation folder to manually verify the touch annotation
        pos_dir = vid.parents[1].joinpath(f'{args.stream}_manual_verification', 'touch')
        pos_dir.mkdir(parents=True, exist_ok=True)

        neg_dir = vid.parents[1].joinpath(f'{args.stream}_manual_verification', 'non_touch')
        neg_dir.mkdir(parents=True, exist_ok=True)



    # Calculate the indices for dividing into thirds
    third_1_end = len(all_frames) // 3
    third_2_end = 2 * len(all_frames) // 3

    # Randomly select 3 frames far apart
    sample_frames = [np.random.choice(all_frames[:third_1_end]),
                        np.random.choice(all_frames[third_1_end:third_2_end]),
                        np.random.choice(all_frames[third_2_end:])]

    bboxes = []

    # Open window for each frame and get bounding box coordinates
    for frame in sample_frames:
        # print(f"Select ROI for {frame}")
        bbox = select_roi(frame)
        if bbox:
            bboxes.append(bbox)

        print(f"ROI selected for {frame.name}: {bbox}")

    if len(bboxes) == 3:
        # Calculate the average bounding box
        u_bbox = union_bboxes(bboxes)
        res['bbox'] = u_bbox
        print(f"Search region bounding box: {u_bbox}")

    else:
        print("Bounding box selection was incomplete. Skip this video.")
        continue

    # Detect touch or non-touch based on the green LED in the average bounding box
    pos_cnt = 0
    neg_cnt = 0
    for frame_path in tqdm(all_frames):
        img = cv2.imread(frame_path)
        img = img[u_bbox[1]:u_bbox[3], u_bbox[0]:u_bbox[2]]
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_green, upper_green)

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










