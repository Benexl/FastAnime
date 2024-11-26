let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  packages = [
    (pkgs.python3.withPackages (python-pkgs: [
      python-pkgs.yt-dlp
      python-pkgs.dbus-python
      python-pkgs.requests
      python-pkgs.rich
      python-pkgs.click
      python-pkgs.inquirerpy
      python-pkgs.mpv
      python-pkgs.fastapi
      python-pkgs.thefuzz
      python-pkgs.plyer
    ]))
  ];
}
