{
description = "FUSE filesystem exposing Twitch live streams via yt-dlp";

inputs = {
nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
flake-utils.url = "github:numtide/flake-utils";
};

outputs = { self, nixpkgs, flake-utils }:
flake-utils.lib.eachDefaultSystem (system:
    let
    pkgs = import nixpkgs { inherit system; };
    in {
    packages.default = pkgs.callPackage ./package.nix {};
    
    apps.default = {
    type = "app";
    program = "${self.packages.${system}.default}/bin/twitchfs";
    };
    }
);
}
