"""
Huy Anh Nguyen
CS PhD @Stony Brook University @University of Adelaide

Created Jan 14, 2025
---------------------
Prepare for I3D feature extraction using video_features github repo.
Convert webcam2.mp4 to Px_Tx_webcam2.mp4.
"""
import argparse
import os
import shutil
from glob import glob

parser = argparse.ArgumentParser(description='Prepare for I3D feature extraction')
parser.add_argument('-i', '--input', type=str, required=False, help='Path to the collected data folder')
parser.add_argument('-o', '--output', type=str, required=False, help='Path to the output folder')

args = parser.parse_args()

all_vids = glob(os.path.join(args.input, '*', '*', 'webcam2.mp4'))
print(f'[INFO] Total {len(all_vids)} videos...')

for vid in all_vids:
    if '.DS_Store' in vid: # annoying macOS
        continue

    # Copy webcam2.mp4 to Px_Tx_webcam2.mp4
    p, t = vid.split('/')[-3], vid.split('/')[-2]
    shutil.copy(vid, os.path.join(args.output, f'{p}_{t}_webcam2.mp4'))
    print(f'[INFO] Copied {vid} to {os.path.join(args.output, f"{p}_{t}_webcam2.mp4")}')


