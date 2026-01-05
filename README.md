# TwitchFS

TwitchFS is a FUSE filesystem that allows you to mount Twitch streams as virtual files. It enables watching Twitch
streams through any media player that can read the files.

## Requirements

- Python 3.6+
- FUSE
- yt-dlp

## Installation

As a Nix User; I actually don't know what the packages for other Distros would be called! Please add to this if you do!
What I do know is that you need:

 - Python 3.6+
  - FUSE3
  - yt-dlp

For Nix(OS) users, you can `nix run` or `nix shell` as long as you have flakes enabled, even if you're not using them, and everything will be set up, as long as you have FUSE set up on your OS.

## Usage

1. Create a mount point:
   ```bash
   mkdir ~/twitch
   ```

2. Mount the filesystem:
   ```bash
   ./twitchfs.py ~/twitch [channels_list_file]
   ```

3. Create directories for channels you want to watch if they're not already present (in the channels list file):
   ```bash
   mkdir ~/twitch/channelname
   ```

4. When a channel is live, a `live.mp4` file will appear in its directory.
   You can open this file with any media player:
   ```bash
   vlc ~/twitch/channelname/live.mp4
   ```
   This is refreshed every 5 minutes. (Note: This is currently single threaded, and checks ALL channels - An improvement would be to thread it and only do the RELEVANT channel!)

## Features

- Automatically detects when channels go live
- Caches live status checks for 5 minutes
- Works with any media player that can read the files (Tested: VLC, MPV)

## Limitations

- Only shows currently live streams
- No Support for loading past streams
- No Support for Chat
- No Support for Cookies from Browsers
- No VOD support (live streams only)

## Contributing

Contributions are welcome! If you're familiar with Python and FUSE, you can help by:

- Adding VOD support
- Implementing chat integration (FILO Text File?)
- Improving error handling
- Adding support for browsers' cookies
- Writing tests
- Threading! All of the Threading!

Please submit pull requests or open issues for any bugs or feature requests.

## License

This project is open source and available under the MIT License.
