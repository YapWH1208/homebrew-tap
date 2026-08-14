# YapWH1208/homebrew-tap

Homebrew tap for [AerialDrop](https://github.com/YapWH1208/AerialDrop) — import your own videos into macOS Tahoe's native Aerial (wallpaper) catalogue.

## Install

```sh
brew install --cask yapwh1208/tap/aerialdrop
```

or, if you prefer to tap first:

```sh
brew tap YapWH1208/tap
brew install --cask aerialdrop
```

If Homebrew asks you to trust the tap first: `brew trust yapwh1208/tap`.

> **⚠️ Disclaimer — unsigned app:** AerialDrop is **ad-hoc signed and not notarized by Apple**. This cask automatically removes the macOS download quarantine (`com.apple.quarantine`) after install so the app opens without Gatekeeper blocking it — that disables Apple's malware check for this app, so you are trusting the publisher instead of Apple. Only install from this official tap (source: [YapWH1208/AerialDrop](https://github.com/YapWH1208/AerialDrop)) and audit the open-source code if you have concerns.

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
