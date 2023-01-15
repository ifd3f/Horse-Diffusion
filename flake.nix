{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = { self, nixpkgs }:
    let
      forAllSystems = nixpkgs.lib.genAttrs [
        "x86_64-linux"
        "x86_64-darwin"
        "aarch64-linux"
        "aarch64-darwin"
      ];

      poetryOverlay = (final: prev: {
        "flickr-api" = prev."flickr-api".overridePythonAttrs
          (old: { buildInputs = old.buildInputs ++ [ prev.setuptools ]; });

        "pleroma-py" = prev."pleroma-py".overridePythonAttrs
          (old: { buildInputs = old.buildInputs ++ [ prev.setuptools ]; });
      });
    in {
      packages = forAllSystems (system:
        let pkgs = nixpkgs.legacyPackages.${system};
        in {
          default = self.packages.${system}.blurred-horse-bot;

          blurred-horse-bot = with pkgs;
            poetry2nix.mkPoetryApplication {
              projectDir = self;
              overrides =
                poetry2nix.defaultPoetryOverrides.extend poetryOverlay;
            };
        });

      devShells = forAllSystems (system:
        let pkgs = nixpkgs.legacyPackages.${system};
        in {
          default = with pkgs;
            mkShellNoCC {
              packages = [
                (poetry2nix.mkPoetryEnv {
                  projectDir = self;
                  overrides =
                    poetry2nix.defaultPoetryOverrides.extend poetryOverlay;
                })
                poetry
              ];
            };
        });
    };
}
