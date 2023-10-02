"""
rsubsync.py

This module provides a command-line interface for synchronizing subtitles with their corresponding video files.
"""

import fnmatch
import os
import subprocess
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument(
    "--lang",
    dest="language_codes",
    required=True,
    nargs="+",
    help="Specify one or more language codes of the subtitles you want to sync (ie. es en...)",
)

parser.add_argument(
    "--path",
    dest="path",
    default=".",
    required=False,
    help="Specify the path to sync. It will be '.' by default (current directory)",
)

args = parser.parse_args()

SETTINGS = {
    "SUBSYNC_PATH": "subsync",
    "PATH_TO_SYNC": args.path,
    "VIDEO_EXTENSIONS": [".mkv", ".mp4", ".avi"],
    "USED_SUBS_FILE": os.path.join(
        os.path.dirname(
            os.path.realpath(__file__)
        ),  # To avoid using the current directory where the script was executed
        "used-subs.txt",
    ),
    "SUBTITLE_EXTENSION_TO_SYNC": [
        f".{lang_code}.srt" for lang_code in args.language_codes
    ],
}


def get_subtitle(root, filename):
    """
    Returns the full path of the subtitle file.
    """
    return os.path.join(root, filename)


def get_file_base(root, filename, extension):
    """
    Returns the full path of the file without the extension.
    """
    return os.path.join(root, filename.split(extension)[0])


def get_matching_video_extension(filename):
    """
    Returns the full path of the video file that matches the given filename.
    """
    video_match = None
    for extension in SETTINGS["VIDEO_EXTENSIONS"]:
        video_file_to_check = f"{filename}{extension}"
        if os.path.exists(video_file_to_check):
            video_match = video_file_to_check
            break
    return video_match


def execute_subsync_process(video, subtitle):
    """
    Executes the subsync process with the given video and subtitle files.
    """
    return subprocess.call(
        [SETTINGS["SUBSYNC_PATH"], video, "-i", subtitle, "--overwrite-input"]
    )


def read_used_subs_file():
    """
    Reads the used-subs.txt file and returns a set of the filenames.
    """
    used_subs = set()
    if os.path.exists(SETTINGS["USED_SUBS_FILE"]):
        with open(SETTINGS["USED_SUBS_FILE"], "r", encoding="utf-8") as f:
            used_subs = set(f.read().splitlines())
    else:
        with open(SETTINGS["USED_SUBS_FILE"], "w", encoding="utf-8") as f:
            f.close()
    return used_subs


def write_used_subs_file(filename):
    """
    Writes the given filename to the used-subs.txt file.
    """
    with open(SETTINGS["USED_SUBS_FILE"], "a", encoding="utf-8") as f:
        f.write(filename + "\n")


def sync_subtitle(subtitle, video_match, filename):
    """
    Synchronizes the given subtitle with the given video file.
    """
    try:
        print(f"Starting sync process of: {subtitle}")
        write_used_subs_file(filename)

        process_code = execute_subsync_process(video_match, subtitle)

        if process_code != 0:
            raise subprocess.CalledProcessError(process_code, "subsync")
    except subprocess.CalledProcessError as e:
        handle_sync_error(subtitle, e)


def video_file_exists(file_base):
    """
    Returns the full path of the video file that matches the given file base.
    """
    video_match = get_matching_video_extension(file_base)
    if video_match is not None:
        return video_match
    print(f"There's no video file for: {file_base}")
    return False


def handle_sync_error(subtitle, error):
    """
    Handles an error that occurred during the synchronization process.
    """
    print(f"There has been an error in the syncing process of: {subtitle}")
    print(f"Error message: {error}")


def main():
    """
    Starts the synchronization process in the specified path.
    """
    print(f"Starting sync process in path: '{SETTINGS['PATH_TO_SYNC']}'")

    try:
        for root, _, filenames in os.walk(f"{SETTINGS['PATH_TO_SYNC']}"):
            for lang_code in SETTINGS["SUBTITLE_EXTENSION_TO_SYNC"]:
                for filename in fnmatch.filter(filenames, f"*{lang_code}"):
                    used_subs = read_used_subs_file()
                    if filename in used_subs:
                        continue
                    subtitle = get_subtitle(root, filename)
                    file_base = get_file_base(root, filename, lang_code)

                    video_match = video_file_exists(file_base)
                    if video_match:
                        sync_subtitle(subtitle, video_match, filename)
    except KeyboardInterrupt:
        print("Exiting application...")
        sys.exit()


if __name__ == "__main__":
    if os.path.exists(SETTINGS["PATH_TO_SYNC"]):
        main()
    else:
        print("Specified path does not exist")
