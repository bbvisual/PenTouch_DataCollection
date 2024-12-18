# PenTouch_DataCollection
Code for Pen-Touch Data Collection project

# Installation
1. Clone the repository
2. Install miniconda from https://docs.conda.io/en/latest/miniconda.html
3. Create a new conda environment:
```
conda create -n aria python=3.11
conda activate aria
pip install beepy obsws-python
```

4. Pair Aria Glass with your computer following [this guide](https://facebookresearch.github.io/projectaria_tools/docs/ARK/sdk/setup)
5. Install Repaper Studio and setup OBS following guide [here]()

# Usage
1. To record using wifi, run:
```
python ./data_collection/script.py -name [filename] -ip [ip_address] -profile [profile_name]
```
Alternatively, you can set the IP address in `DEFAULT_IP` variable in the script.py file.
By default, Aria Glass is set to `profile28`. You can change the profile by setting the `DEFAULT_PROFILE` variable in the script.py file.
List of profiles can be found [here](https://facebookresearch.github.io/projectaria_tools/docs/tech_spec/recording_profiles)

To record using USB, run:
```
python ./data_collection/script.py -name [filename] -wired
```

2. To process the recorded data, run:
[TBD]
