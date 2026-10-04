cask "aerialdrop" do
  # BEGIN GENERATED COMPATIBILITY
  on_tahoe :or_newer do
    version "1.1.9"
    sha256 "e15c54590650c57d3c91492c85b080fd7911f582397b54b3e0973fedbcff20c2"
    url "https://github.com/YapWH1208/AerialDrop/releases/download/v1.1.9/AerialDrop-1.1.9-macOS.zip"
  end

  depends_on macos: :tahoe
  depends_on arch: :arm64
  # END GENERATED COMPATIBILITY

  name "AerialDrop"
  desc "Import your own videos into the native Aerial wallpaper catalogue"
  homepage "https://github.com/YapWH1208/AerialDrop"

  # Homebrew considers any different installed version outdated, even when the
  # selected version is older. Disable that downgrade before upgrade preflight
  # moves the installed app. Uninstall still works; fresh install then clears it.
  installed_release = cask.installed_version
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
