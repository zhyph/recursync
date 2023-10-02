import fnmatch
import os
import subprocess
import argparse
import subprocess

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
    "FAILED_SUFFIX": ".failed",
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
    return os.path.join(root, filename)


def get_file_base(root, filename, extension):
    return os.path.join(root, filename.split(extension)[0])


def get_matching_video_extension(filename):
    video_match = None
    for extension in SETTINGS["VIDEO_EXTENSIONS"]:
        video_file_to_check = f"{filename}{extension}"
        if os.path.exists(video_file_to_check):
            video_match = video_file_to_check
            break
    return video_match


def execute_subsync_process(video, subtitle):
    return subprocess.call(
        [SETTINGS["SUBSYNC_PATH"], video, "-i", subtitle, "--overwrite-input"]
    )


def read_used_subs_file():
    used_subs = set()
    if os.path.exists(SETTINGS["USED_SUBS_FILE"]):
        with open(SETTINGS["USED_SUBS_FILE"], "r") as f:
            used_subs = set(f.read().splitlines())
    else:
        open(SETTINGS["USED_SUBS_FILE"], "w").close()
    return used_subs


def write_used_subs_file(filename):
    with open(SETTINGS["USED_SUBS_FILE"], "a") as f:
        f.write(filename + "\n")


def main():
    print(f"Starting sync process in path: {SETTINGS['PATH_TO_SYNC']}...")
    used_subs = read_used_subs_file()
    try:
        for root, dirnames, filenames in os.walk(f"{SETTINGS['PATH_TO_SYNC']}"):
            for lang_code in SETTINGS["SUBTITLE_EXTENSION_TO_SYNC"]:
                for filename in fnmatch.filter(filenames, f"*{lang_code}"):
                    if filename in used_subs:
                        continue
                    subtitle = get_subtitle(root, filename)
                    file_base = get_file_base(root, filename, lang_code)
                    video_match = get_matching_video_extension(file_base)

                    if video_match is not None:
                        try:
                            print(f"Starting sync process of: {filename}")
                            write_used_subs_file(filename)
                            used_subs = read_used_subs_file()

                            process_code = execute_subsync_process(
                                video_match, subtitle
                            )

                            if process_code != 0:
                                raise subprocess.CalledProcessError(
                                    process_code, "subsync"
                                )
                        except subprocess.CalledProcessError as e:
                            print(
                                f"There has been an error in the syncing process of: {filename}"
                            )
                            print(f"Error message: {e}")
                    else:
                        print(f"There's no video file for: {filename}")
    except KeyboardInterrupt:
        print("Exiting application...")
        exit()


if __name__ == "__main__":
    if os.path.exists(SETTINGS["PATH_TO_SYNC"]):
        main()
    else:
        print("Specified path does not exist")
