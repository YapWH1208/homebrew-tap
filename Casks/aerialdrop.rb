cask "aerialdrop" do
  version "1.1.4"
  sha256 "09c7d26f99540919d3040e83a1118ac11b11de56d745fe0b10e4c0e66fdf4ece"

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
