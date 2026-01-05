#!/usr/bin/env python3
import os
import errno
import stat
import subprocess
import time
from fuse import FUSE, Operations, FuseOSError

TWITCH_ROOT = "."
LIVE_FILE = "live.mp4"
CACHE_TTL = 300  # Cache live status for 5 minutes

class TwitchFS(Operations):
    def __init__(self, initial_channels=None):
        self.channels = set(initial_channels or [])
        self.streams = {}  # fh -> subprocess
        self._live_cache = {} # channel -> (is_live, timestamp)

    # ---------------
    # Helpers
    # ---------------

    def _split(self, path):
        return [p for p in path.split("/") if p]

    def _is_live(self, channel):
        now = time.time()
        if channel in self._live_cache:
            is_live, timestamp = self._live_cache[channel]
            if now - timestamp < CACHE_TTL:
                return is_live

        try:
            result = subprocess.run(
                [
                    "yt-dlp",
                    "--quiet",
                    "--no-warnings",
                    "--print",
                    "is_live",
                    f"https://www.twitch.tv/{channel}",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            is_live = result.stdout.strip().lower() == "true"
            self._live_cache[channel] = (is_live, now)
            return is_live
        except Exception:
            return False

    # ---------------------------
    # Filesystem ops
    # ---------------------------

    def getattr(self, path, fh=None):
        parts = self._split(path)

        if path == "/":
            return dict(st_mode=(stat.S_IFDIR | 0o755), st_nlink=2)

        if path == "/":
            return dict(st_mode=(stat.S_IFDIR | 0o755), st_nlink=2)

        if len(parts) == 1:
            # We don't check self.channels here to allow mkdir to work correctly
            # and to allow access to cached channel names.
            return dict(st_mode=(stat.S_IFDIR | 0o755), st_nlink=2)

        if len(parts) == 2:
            channel = parts[0]
            filename = parts[1]
            if filename == LIVE_FILE and self._is_live(channel):
                return dict(
                    st_mode=(stat.S_IFREG | 0o444),
                    st_nlink=1,
                    st_size=10**10, # Return large size to avoid VLC EINVAL/seek issues
                )

        raise FuseOSError(errno.ENOENT)

    def open(self, path, flags):
        parts = self._split(path)

        if len(parts) == 2:
            channel = parts[0]
            filename = parts[1]

            if filename == LIVE_FILE:
                # We do the is_live check here to be sure
                if self._is_live(channel):
                    proc = subprocess.Popen(
                        [
                            "yt-dlp",
                            f"https://www.twitch.tv/{channel}",
                            "--cookies-from-browser",
                            "firefox",
                            "-o",
                            "-",
                        ],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL,
                    )

                    if proc:
                        fh = proc.pid
                        self.streams[fh] = proc
                        return fh

        raise FuseOSError(errno.ENOENT)

    def read(self, path, size, offset, fh):
        proc = self.streams.get(fh)
        if not proc:
            return os.strerror(errno.EBADF)

        return proc.stdout.read(size)

    def release(self, path, fh):
        proc = self.streams.pop(fh, None)
        if proc:
            proc.terminate()
            # proc.wait() # blocking
        return
    
    def readdir(self, path, fh):
        parts = self._split(path)

        yield "."
        yield ".."

        if path == "/":
            for c in sorted(self.channels):
                yield c
            return

        if len(parts) == 1:
            channel = parts[0]
            #if channel in self.channels and self._is_live(channel):
            if self._is_live(channel):
                yield LIVE_FILE
            return

        raise FuseOSError(errno.ENOENT)

    def mkdir(self, path, mode):
        parts = self._split(path)

        if len(parts) == 1:
            self.channels.add(parts[0])
            return

        raise FuseOSError(errno.EPERM)

    def rmdir(self, path):
        parts = self._split(path)

        if len(parts) == 1:
            self.channels.discard(parts[0])
            return

        raise FuseOSError(errno.EPERM)


def main(mountpoint, channels_file=None):
    initial_channels = []
    if channels_file and os.path.exists(channels_file):
        with open(channels_file, 'r') as f:
            initial_channels = [line.strip() for line in f if line.strip()]

    FUSE(
        TwitchFS(initial_channels=initial_channels),
        mountpoint,
        foreground=True,
        ro=False,
        allow_other=False,
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} <mountpoint> [channels_list_file]")
        sys.exit(1)

    channels_path = sys.argv[2] if len(sys.argv) > 2 else None
    main(sys.argv[1], channels_path)
