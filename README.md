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

## Gatekeeper

AerialDrop is ad-hoc signed (no paid Apple Developer ID), so macOS would normally refuse the first launch after download. The cask's `postflight` removes the download quarantine automatically, so `brew install --cask aerialdrop` (and upgrades) just work.

If you install the raw release zip instead, clear the quarantine yourself:

```sh
xattr -dr com.apple.quarantine /Applications/AerialDrop.app
```

or right-click → **Open** once. This is the free alternative to Apple notarization, which requires a \$99/year Developer account.

## Updating

The cask is bumped automatically from new [GitHub Releases](https://github.com/YapWH1208/AerialDrop/releases) (checked daily); the *Update cask* workflow can also be run manually from the Actions tab. On your machine: `brew update && brew upgrade --cask aerialdrop`.

## Requirements

macOS Tahoe (26) or later.
