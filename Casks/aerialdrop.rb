cask "aerialdrop" do
  version "1.1.8"
  sha256 "ded9fa9780986a024cbc4fabfaee5ff3ca94870e7423962c331f1bf6a2dd3520"

  url "https://github.com/YapWH1208/AerialDrop/releases/download/v#{version}/AerialDrop-#{version}-macOS.zip"
  name "AerialDrop"
  desc "Import your own videos into the native Aerial wallpaper catalogue"
  homepage "https://github.com/YapWH1208/AerialDrop"

  livecheck do
    url :url
    strategy :github_latest
  end

  depends_on macos: :tahoe

  app "AerialDrop.app"

  postflight do
    # AerialDrop is ad-hoc signed and not notarized (no paid Apple Developer
    # account), so a download quarantine attribute makes Gatekeeper refuse the
    # first launch. Remove it so brew installs just open.
    system_command "xattr",
                   args: ["-dr", "com.apple.quarantine", appdir.join("AerialDrop.app").to_s]
  end

  zap trash: [
    "~/Library/Application Support/com.apple.wallpaper/aerials/AerialDropBackups",
    "~/Library/Application Support/com.apple.wallpaper/Store/AerialDropBackups",
    "~/Library/Preferences/com.yapwh.aerialdrop.plist",
  ]
end
