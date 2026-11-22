cask "aerialdrop" do
  # BEGIN GENERATED COMPATIBILITY
  on_tahoe :or_newer do
    version "1.1.11"
    sha256 "fd4714c5cb1185f278a2469ba2a86973cc6666b3854b1fc2a98d70a9a788f243"
    url "https://github.com/YapWH1208/AerialDrop/releases/download/v1.1.11/AerialDrop-1.1.11-macOS.zip"
  end

  depends_on macos: :tahoe
  depends_on arch: :arm64
  # END GENERATED COMPATIBILITY

  name "AerialDrop"
  desc "Import your own videos into the native Aerial wallpaper catalogue"
  homepage "https://github.com/YapWH1208/AerialDrop"
  auto_updates true

  # Homebrew considers any different installed version outdated, even when the
  # selected version is older. Disable that downgrade before upgrade preflight
  # moves the installed app. Uninstall still works; fresh install then clears it.
  installed_release = self.cask.installed_version
  if version.nil?
    disable! date: "2026-10-04",
             because: "has no compatible published release for this macOS version"
  elsif installed_release && Version.new(installed_release) > Version.new(version.to_s)
    disable! date: "2026-10-04",
             because: "would downgrade installed AerialDrop #{installed_release} to compatible #{version}; " \
                      "uninstall it first if you deliberately want to install #{version}"
  end

  livecheck do
    skip "Updates are selected per macOS version from AerialDrop's compatibility policy"
  end

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
