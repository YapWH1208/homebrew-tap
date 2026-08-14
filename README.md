# homebrew-aerialdrop

Homebrew tap for [AerialDrop](https://github.com/YapWH1208/AerialDrop) — import your own videos into macOS Tahoe's native Aerial (wallpaper) catalogue.

## Install

```sh
brew tap YapWH1208/homebrew-aerialdrop
brew install --cask aerialdrop
```

or in a single command:

```sh
brew install --cask YapWH1208/homebrew-aerialdrop/aerialdrop
```

## First launch

AerialDrop is ad-hoc signed. The first launch may need **right-click → Open** on `AerialDrop.app` in /Applications (or install with `brew install --cask --no-quarantine aerialdrop`).

## Updating

The cask is bumped automatically from new [GitHub Releases](https://github.com/YapWH1208/AerialDrop/releases) (checked daily); the *Update cask* workflow can also be run manually from the Actions tab. On your machine: `brew update && brew upgrade --cask aerialdrop`.

## Requirements

macOS Tahoe (26) or later.
