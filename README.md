# r-subsync

Script to recursively sync (using [Subsync](https://github.com/smacke/subsync)) all the subtitles of a folder and overwrite the old one (after backing it up). It won't try to sync previously synced subs on next iterations.

[Subsync](https://github.com/smacke/subsync) is an awesome library, I highly recommend you to check out its repository:

History about it:

"The implementation for this project was started during HackIllinois 2019, for which it received an Honorable Mention (ranked in the top 5 projects, excluding projects that won company-specific prizes)."

## Requirements

- Python 3.6+
- [Subsync](https://github.com/smacke/subsync)

## Usage

`python rsubsync.py --lang xx --path /path`
Only the `lang` is required. It needs to match the lang specified on your subtitle files, and more than one language can be passed, so:

If your subtitles are named like:
`subtitle.en.srt`, `subtitle2.es.srt`
the lang needs to be
`en` if you only want `.en.srt` to be processed, or `en es` (order does not matter if you don't care which one goes first) if you want both files to be processed.

## Example usage

P.S. On this forked version:

- The script is going to overwrite your 'old' srt file, if you don't want that behavior, go to the original forked repo and use his script that creates extra files to avoid the overwrite of the current one.
- A file named `used-subs.txt` will be created at the root of the cloned repo to simulate the behavior from `filebot` and ignore already processed files to avoid redundancy, if you wish to ignore that and always process the same files as before just comment out lines: `88-89` and if you want to complete remove the read/write to the `used-subs.txt` file, comment out: `83, 97-98` too.

Having:

```text
.
└── path-to-sync-recursively
    ├── video1
    │   ├── video1.en.srt
    |   ├── video1.es.srt
    │   └── video1.mkv
    └── video2
        ├── video2.en.srt
        └── video2.mkv
```

Using the command:

`python3 rsubsync.py --lang en es --path /path-to-sync-recursively/`

Will do this (nothing with this script):

```text
.
└── path-to-sync-recursively
    ├── video1
    │   ├── video1.en.srt
    │   └── video1.mkv
    └── video2
        ├── video2.en.srt
        └── video2.mkv
```

As you can see no new files you be added, overriding the 'old' ones.
In case there are errors in the process of syncing any subtitle, this script will not do anything special, just keep going.
If you don't specify any `path` it will use the current one (`'.'`) to start syncing.
