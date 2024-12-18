import argparse
import time

import aria.sdk as aria
import beepy
import obsws_python as obs

DEFAULT_IP = '192.168.8.6'
DEFAULT_PROFILE = 'profile28'

parser = argparse.ArgumentParser()

parser.add_argument("-n", "--name", help="Name of the recording file", default="test")
parser.add_argument(
    "-ip", help="IP address to connect to the device over wifi", default=DEFAULT_IP
)  # default for DARPA
parser.add_argument('-wired', help="Use wired connection", action='store_true')
parser.add_argument(
    "-profile", help="Profile to be used for streaming.", default=DEFAULT_PROFILE
)

aria.set_log_level(aria.Level.Info)


class Aria:
    def __init__(self, ip, profile):
        self.ip = ip
        self.device_config = aria.DeviceClientConfig()
        self.device_config.ip_v4_address = self.ip

        self.recording_config = aria.RecordingConfig()
        self.recording_config.profile_name = profile

        self.device_client = aria.DeviceClient()
        self.device_client.set_client_config(self.device_config)

        self.connect()

    def connect(self):
        self.device = self.device_client.connect()
        self.recording_manager = self.device.recording_manager
        self.recording_manager.recording_config = self.recording_config

        status = self.device.status
        # Print device status
        if self.ip:
            print(
                f"[INFO] WiFi Mode >>> Aria Device Status: battery level {status.battery_level}, wifi ssid {status.wifi_ssid}, wifi ip {status.wifi_ip_address}, mode {status.device_mode}"
            )
        else:
            print(
                f"[INFO] USB Mode >>> Aria Device Status: battery level {status.battery_level}, mode {status.device_mode}"
            )

    def disconnect(self):
        self.device_client.disconnect(self.device)
        print("[INFO] Disconnected from Aria")

    def start_recording(self):
        if self.is_recording():
            print("[WARNING] Glasses are already recording. Use app to stop recording first")
            exit(1)

        self.recording_manager.start_recording()
        print("[INFO] Started Aria recording")

    def stop_recording(self):
        self.recording_manager.stop_recording()
        print("[INFO] Stopped Aria recording")

    def is_recording(self):
        return self.recording_manager.recording_state == aria.RecordingState.Recording


class OBS:
    def __init__(self, host="localhost", port=4455):
        self.client = obs.ReqClient(host=host, port=port)

    def start_recording(self, file_name=None):
        if file_name:
            self.client.set_profile_parameter("Output", "FilenameFormatting", file_name)

        self.client.start_record()
        print(f"[INFO] Started OBS recording with output {file_name}")

    def stop_recording(self):
        self.client.stop_record()
        print("[INFO] Stopped OBS recording")

if __name__ == "__main__":
    args = parser.parse_args()
    if args.wired:
        print("[INFO] Using wired connection")
        args.ip = ''

    aria_glass = Aria(args.ip, args.profile)
    obs = OBS()

    # Start recording on both devices
    aria_glass.start_recording()
    obs.start_recording(args.name)
    time.sleep(1)

    # Play synchronization sound
    beepy.beep(sound=5)

    # Clear any pending input
    print("\n[INFO] Recording in progress. Press 'q' and Enter to stop recording...")

    while True:
        user_input = input().lower()
        if user_input == 'q':
            print("[INFO] Stopping recording...")
            try:
                beepy.beep(sound=5)
                aria_glass.stop_recording()
                obs.stop_recording()
                aria_glass.disconnect()

                print("[INFO] All recordings stopped successfully")
                break
            except Exception as e:
                print(f"[ERROR] Error during shutdown: {e}")
                # Still try to continue with remaining cleanup
