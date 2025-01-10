"""
Huy Anh Nguyen
CS PhD @Stony Brook University @University of Adelaide

Created Jan 2, 2025
---------------------
Convert VRS to MP4 using provided Aria Glasses tool.

Expect input folder structure similar to EPIC-KITCHENS:
Dec30
├── P1
│   ├── T1
│   │   ├── aria.vrs
│   │   ├── aria.vrs.json
│   │   ├── screen.png      <- from Repaper Studio
│   │   └── obs.mp4         <- from OBS
│   ├── T2 ...
"""
import argparse
import os
import subprocess
from glob import glob

parser = argparse.ArgumentParser(description='Convert VRS to MP4 using provided Aria Glasses tool.')
parser.add_argument('-i', '--input', type=str, required=True, help='Path to the collected data folder')

args = parser.parse_args()

# args.input = 'SOMETIME' # for manual run

all_vrs = sorted(glob(os.path.join(args.input, '*', '*', '*.vrs')))
print('[INFO] Found', len(all_vrs), 'VRS files...')

for idx, vrs in enumerate(all_vrs):
    print(f'Processing {idx+1}/{len(all_vrs)}: {vrs}')
    out_file = os.path.join(os.path.dirname(vrs), 'aria.mp4')
    command = [
    "vrs_to_mp4",
    "--vrs", vrs,
    "--output_video", out_file
]
    subprocess.run(command, check=True)
