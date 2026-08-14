# YapWH1208/homebrew-tap

Homebrew tap for [YapWH1208](https://github.com/YapWH1208)'s open-source macOS apps.

## Using this tap

Add the tap once:

```sh
brew tap YapWH1208/tap
```

or install a cask directly without tapping first:

```sh
brew install --cask yapwh1208/tap/<cask>
```

If Homebrew asks you to trust the tap first, run `brew trust yapwh1208/tap`.

## Available casks

### aerialdrop — [AerialDrop](https://github.com/YapWH1208/AerialDrop)

Import your own videos into macOS Tahoe's native Aerial (wallpaper) catalogue.

```sh
brew install --cask yapwh1208/tap/aerialdrop
```

> **⚠️ Disclaimer — unsigned app:** AerialDrop is **ad-hoc signed and not notarized by Apple**. This cask automatically removes the macOS download quarantine (`com.apple.quarantine`) after install so the app opens without Gatekeeper blocking it — that disables Apple's malware check for this app, so you are trusting the publisher instead of Apple. Only install from this official tap (source: [YapWH1208/AerialDrop](https://github.com/YapWH1208/AerialDrop)) and audit the open-source code if you have concerns.

If you install AerialDrop from the raw release zip instead, clear the quarantine yourself with `xattr -dr com.apple.quarantine /Applications/AerialDrop.app`, or right-click → **Open** once. This is the free alternative to Apple notarization, which requires a \$99/year Developer account.

## Updating

Casks are bumped automatically from each app's GitHub Releases (checked daily); each cask's update workflow can also be run manually from the Actions tab. On your machine: `brew update && brew upgrade --cask <cask>`.

## Adding a new app

1. Add `Casks/<cask>.rb` — model it on [`Casks/aerialdrop.rb`](Casks/aerialdrop.rb) (version + sha256 from the app's GitHub release, `app` stanza, `postflight` for unsigned apps, `livecheck`, `zap`).
2. Add a per-cask update workflow in `.github/workflows/` — model it on `update-cask.yml`, pointing at the new app's releases and cask file.

## Requirements

macOS Tahoe (26) or later for AerialDrop (varies per cask).
