{
  description = "FastAnime Project Flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }: flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs { inherit system; };

      python = pkgs.python312;
      pythonPackages = python.pkgs;
      fastanimeEnv = pythonPackages.buildPythonApplication {
        pname = "fastanime";
        version = "2.8.8";

        src = self;

        preBuild = ''
          sed -i 's/rich>=13.9.2/rich>=13.8.1/' pyproject.toml
          sed -i 's/pycryptodome>=3.21.0/pycryptodome>=3.20.0/' pyproject.toml
        '';

        # Add runtime dependencies
        propagatedBuildInputs = with pythonPackages; [
          click
          inquirerpy
          requests
          rich
          thefuzz
          yt-dlp
          dbus-python
          hatchling
          plyer
          mpv
          fastapi
          pycryptodome
          pypresence
        ];

        # Ensure compatibility with the pyproject.toml
        format = "pyproject";
      };

    in
    {
      packages.default = fastanimeEnv;

      # DevShell for development
      devShells.default = pkgs.mkShell {
        LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [ pkgs.libxcrypt-legacy ];
        buildInputs = [
          fastanimeEnv
          pythonPackages.hatchling
          pkgs.mpv
          pkgs.fzf
          pkgs.rofi
          pkgs.uv
          pkgs.pyright
        ];
        shellHook = ''
          uv venv -q
          source ./.venv/bin/activate
        '';
      };
    });
}
