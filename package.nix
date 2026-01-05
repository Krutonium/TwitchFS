{ lib
, python3
, yt-dlp
, fuse3
}:

python3.pkgs.buildPythonApplication {
  pname = "twitchfs";
  version = "0.1.0";

  format = "other";

  src = ./.;

  propagatedBuildInputs = with python3.pkgs; [
    fusepy
  ];

  buildInputs = [
    fuse3
  ];

  postInstall = ''
    install -Dm755 twitchfs.py $out/bin/twitchfs
  '';

  makeWrapperArgs = [
    "--prefix PATH : ${lib.makeBinPath [ yt-dlp fuse3 ]}"
  ];

  meta = with lib; {
    description = "FUSE filesystem that exposes Twitch live streams as files";
    platforms = platforms.linux;
    license = licenses.mit;
  };
}
