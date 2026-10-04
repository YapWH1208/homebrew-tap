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

Import your own videos into macOS Tahoe's native Aerial (wallpaper) catalogue. The cask selects the newest officially published ZIP declared compatible with your macOS major version. Its version, URL, and SHA-256 are stored in the cask when the update workflow runs, so installation does not fetch compatibility metadata.

```sh
brew install --cask yapwh1208/tap/aerialdrop
```

> **⚠️ Disclaimer — unsigned app:** AerialDrop is **ad-hoc signed and not notarized by Apple**. This cask automatically removes the macOS download quarantine (`com.apple.quarantine`) after install so the app opens without Gatekeeper blocking it — that disables Apple's malware check for this app, so you are trusting the publisher instead of Apple. Only install from this official tap (source: [YapWH1208/AerialDrop](https://github.com/YapWH1208/AerialDrop)) and audit the open-source code if you have concerns.

If you install AerialDrop from the raw release zip instead, clear the quarantine yourself with `xattr -dr com.apple.quarantine /Applications/AerialDrop.app`, or right-click → **Open** once. This is the free alternative to Apple notarization, which requires a \$99/year Developer account.

## Updating

The AerialDrop cask update workflow checks the app's [compatibility policy](https://github.com/YapWH1208/AerialDrop/blob/main/docs/release-compatibility.json) and all official published releases daily. It can also be run manually from the Actions tab. On your machine: `brew update && brew upgrade --cask aerialdrop`.

An older macOS may continue to receive an earlier AerialDrop version after a newer macOS gets a new release. If you installed a newer AerialDrop version on another macOS and then moved back to an older macOS, Homebrew will refuse to downgrade it during an ordinary upgrade. To deliberately install the version selected for your current macOS, uninstall AerialDrop first and then install the cask again. Uninstalling the app does not remove your imported wallpapers unless you use `--zap`.

For an offline check of cask generation, run `python3 Scripts/update-aerialdrop.py --policy-file <policy.json> --releases-file <releases.json>` with a GitHub releases API catalogue. Run its focused tests with `python3 -m unittest discover -s Tests -p 'test_*.py'`.

## Adding a new app

1. Add `Casks/<cask>.rb` with the app's version and SHA-256, `app` stanza, relevant install steps, and `zap` entries.
2. Add a per-cask update workflow in `.github/workflows/` suited to that app's release and compatibility policy.

## Requirements

macOS Tahoe (26) or later on Apple silicon for AerialDrop (varies per cask).
