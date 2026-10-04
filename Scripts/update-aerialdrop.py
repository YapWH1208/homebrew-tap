#!/usr/bin/env python3
"""Regenerate the static AerialDrop cask from official compatibility metadata.

The release selection below mirrors AerialDrop's release_compatibility.py.
Tests compare it with that canonical resolver using the shared fixture.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


REPOSITORY = "YapWH1208/AerialDrop"
API = f"https://api.github.com/repos/{REPOSITORY}"
RAW = f"https://raw.githubusercontent.com/{REPOSITORY}"
BASE_URL = f"https://github.com/{REPOSITORY}/releases/download"
CASK = Path(__file__).resolve().parent.parent / "Casks/aerialdrop.rb"
BEGIN = "  # BEGIN GENERATED COMPATIBILITY\n"
END = "  # END GENERATED COMPATIBILITY\n"
VERSION_RE = re.compile(r"(0|[1-9][0-9]{0,5})\.(0|[1-9][0-9]{0,5})\.(0|[1-9][0-9]{0,5})\Z")
DIGEST_RE = re.compile(r"sha256:([0-9a-fA-F]{64})\Z")
ARCHITECTURES = frozenset(("arm64", "x86_64"))
# Add a symbol only after the Homebrew cask DSL supports that macOS release.
MACOS_SYMBOLS = {26: "tahoe", 27: "golden_gate"}


class CompatibilityError(ValueError):
    """The policy, release catalogue, or selected Homebrew mapping is invalid."""


def version_key(version: str) -> tuple[int, int, int]:
    if not isinstance(version, str) or (match := VERSION_RE.fullmatch(version)) is None:
        raise CompatibilityError(f"invalid stable version: {version!r}")
    return tuple(int(part) for part in match.groups())


def major(value: Any, label: str) -> int:
    if type(value) is not int or not 26 <= value <= 999:
        raise CompatibilityError(f"{label} must be an integer from 26 through 999")
    return value


def validate_policy(policy: Any) -> dict[str, Any]:
    if not isinstance(policy, dict) or set(policy) != {"schema_version", "releases"}:
        raise CompatibilityError("policy must contain only schema_version and releases")
    if type(policy["schema_version"]) is not int or policy["schema_version"] != 1:
        raise CompatibilityError("unsupported compatibility policy schema_version")
    records = policy["releases"]
    if not isinstance(records, list) or not records:
        raise CompatibilityError("policy releases must be a nonempty array")
    versions: set[str] = set()
    for index, record in enumerate(records):
        label = f"releases[{index}]"
        if not isinstance(record, dict) or set(record) != {
            "version", "min_macos", "max_macos", "architectures"
        }:
            raise CompatibilityError(f"{label} has invalid fields")
        version = record["version"]
        version_key(version)
        if version in versions:
            raise CompatibilityError(f"duplicate compatibility version: {version}")
        versions.add(version)
        minimum = major(record["min_macos"], f"{label}.min_macos")
        maximum = record["max_macos"]
        if maximum is not None and major(maximum, f"{label}.max_macos") < minimum:
            raise CompatibilityError(f"{label}.max_macos is below min_macos")
        architectures = record["architectures"]
        if (not isinstance(architectures, list) or not architectures
                or any(not isinstance(arch, str) or arch not in ARCHITECTURES
                       for arch in architectures)
                or len(architectures) != len(set(architectures))):
            raise CompatibilityError(f"{label}.architectures must contain unique supported architectures")
    return policy


def compatible(record: dict[str, Any], macos: int, arch: str) -> bool:
    major(macos, "macos")
    if arch not in ARCHITECTURES:
        raise CompatibilityError(f"unsupported architecture: {arch!r}")
    return (record["min_macos"] <= macos
            and (record["max_macos"] is None or macos <= record["max_macos"])
            and arch in record["architectures"])


def validated_asset(release: dict[str, Any], version: str) -> dict[str, Any] | None:
    assets = release.get("assets")
    if not isinstance(assets, list):
        return None
    name = f"AerialDrop-{version}-macOS.zip"
    matches = [asset for asset in assets if isinstance(asset, dict) and asset.get("name") == name]
    if len(matches) != 1:
        return None
    asset = matches[0]
    digest = asset.get("digest")
    url = f"{BASE_URL}/v{version}/{name}"
    if (not isinstance(digest, str) or DIGEST_RE.fullmatch(digest) is None
            or type(asset.get("size")) is not int or asset["size"] <= 0
            or asset.get("browser_download_url") != url):
        return None
    return {"name": name, "url": url, "sha256": digest[7:].lower(), "size": asset["size"]}


def resolve_release(policy: Any, catalogue: Any, macos: int, arch: str) -> dict[str, Any]:
    validate_policy(policy)
    major(macos, "macos")
    if arch not in ARCHITECTURES:
        raise CompatibilityError(f"unsupported architecture: {arch!r}")
    if not isinstance(catalogue, list):
        raise CompatibilityError("release catalogue must be an array")
    declarations = {record["version"]: record for record in policy["releases"]}
    candidates: list[dict[str, Any]] = []
    seen_tags: set[str] = set()
    for index, release in enumerate(catalogue):
        if not isinstance(release, dict):
            raise CompatibilityError(f"release catalogue entry {index} must be an object")
        tag = release.get("tag_name")
        if not isinstance(tag, str):
            raise CompatibilityError(f"release catalogue entry {index} has no tag_name")
        if tag in seen_tags:
            raise CompatibilityError(f"duplicate release catalogue tag: {tag}")
        seen_tags.add(tag)
        if not tag.startswith("v"):
            continue
        candidate_version = tag[1:]
        try:
            version_key(candidate_version)
        except CompatibilityError:
            continue
        record = declarations.get(candidate_version)
        if record is None or not compatible(record, macos, arch):
            continue
        if (release.get("draft") is not False or release.get("prerelease") is not False
                or not isinstance(release.get("published_at"), str)
                or not release["published_at"]):
            continue
        asset = validated_asset(release, candidate_version)
        if asset is not None:
            candidates.append({"version": candidate_version, "tag": tag, "asset": asset})
    if not candidates:
        raise CompatibilityError(f"no compatible published release for macOS {macos} on {arch}")
    return max(candidates, key=lambda item: version_key(item["version"]))


def selected_or_none(policy: Any, catalogue: Any, macos: int, arch: str) -> dict[str, Any] | None:
    try:
        return resolve_release(policy, catalogue, macos, arch)
    except CompatibilityError as error:
        if str(error).startswith("no compatible published release for "):
            return None
        raise


def symbol(macos: int) -> str:
    try:
        return MACOS_SYMBOLS[macos]
    except KeyError as error:
        raise CompatibilityError(
            f"macOS {macos} requires a Homebrew on_<system> DSL symbol; "
            "update MACOS_SYMBOLS after Homebrew supports it"
        ) from error


def generate_stanzas(policy: Any, catalogue: Any) -> str:
    validate_policy(policy)
    # One cask architecture requirement can express single-architecture releases.
    # A future mixed-architecture policy needs explicit per-arch cask branches.
    architectures = set().union(*(record["architectures"] for record in policy["releases"]))
    if len(architectures) != 1:
        raise CompatibilityError(
            "policy declares multiple architectures; add per-architecture cask branches "
            "before updating this tap"
        )
    arch = architectures.pop()
    boundaries = {record["min_macos"] for record in policy["releases"]}
    boundaries.update(record["max_macos"] + 1 for record in policy["releases"]
                      if record["max_macos"] is not None)
    starts = sorted(boundaries)
    selection = {start: selected_or_none(policy, catalogue, start, arch) for start in starts}
    if not any(selection.values()):
        raise CompatibilityError(f"no published release in policy for {arch}")

    # Each release's compatibility changes only at a min_macos or max_macos + 1.
    # Emit exact branches for finite intervals and :or_newer only for the final
    # unbounded interval. A gap gets no branch, so Homebrew cannot pick a wrong ZIP.
    intervals: list[tuple[int, int | None, dict[str, Any] | None]] = []
    for index, start in enumerate(starts):
        selected = selection[start]
        end = starts[index + 1] if index + 1 < len(starts) else None
        if intervals and intervals[-1][2] == selected:
            previous_start, _, previous_selected = intervals[-1]
            intervals[-1] = (previous_start, end, previous_selected)
        else:
            intervals.append((start, end, selected))

    lines: list[str] = []
    for start, end, selected in intervals:
        if selected is None:
            continue
        if end is None:
            majors = [start]
            modifier = " :or_newer"
        else:
            majors = range(start, end)
            modifier = ""
        for macos in majors:
            lines.extend((
                f"  on_{symbol(macos)}{modifier} do",
                f'    version "{selected["version"]}"',
                f'    sha256 "{selected["asset"]["sha256"]}"',
                f'    url "{selected["asset"]["url"]}"',
                "  end",
                "",
            ))
    minimum = min(start for start in starts if selection[start] is not None)
    lines.extend((
        f"  depends_on macos: :{symbol(minimum)}",
        f"  depends_on arch: :{'arm64' if arch == 'arm64' else 'x86_64'}",
    ))
    return "\n".join(lines) + "\n"


def update_cask(cask: Path, policy: Any, catalogue: Any) -> bool:
    original = cask.read_text(encoding="utf-8")
    if original.count(BEGIN) != 1 or original.count(END) != 1:
        raise CompatibilityError(f"{cask} must contain one generated compatibility section")
    before, remainder = original.split(BEGIN, 1)
    _, after = remainder.split(END, 1)
    updated = before + BEGIN + generate_stanzas(policy, catalogue) + END + after
    if updated == original:
        return False
    cask.write_text(updated, encoding="utf-8")
    return True


def get_json(url: str, token: str | None = None) -> Any:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "AerialDrop-Homebrew-updater"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        with urlopen(Request(url, headers=headers), timeout=30) as response:
            return json.load(response)
    except (HTTPError, URLError, json.JSONDecodeError) as error:
        raise CompatibilityError(f"cannot fetch official release metadata from {url}: {error}") from error


def fetch_official_data(token: str | None) -> tuple[Any, Any]:
    branch = get_json(f"{API}/branches/main", token)
    try:
        commit = branch["commit"]["sha"]
    except (KeyError, TypeError) as error:
        raise CompatibilityError("official main branch response has no commit SHA") from error
    if not isinstance(commit, str) or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise CompatibilityError("official main branch returned an invalid commit SHA")
    policy = get_json(f"{RAW}/{commit}/docs/release-compatibility.json")
    catalogue: list[Any] = []
    for page in range(1, 101):
        batch = get_json(f"{API}/releases?per_page=100&page={page}", token)
        if not isinstance(batch, list):
            raise CompatibilityError(f"official releases page {page} is not an array")
        if len(batch) > 100:
            raise CompatibilityError(f"official releases page {page} exceeds 100 entries")
        catalogue.extend(batch)
        if len(batch) < 100:
            return policy, catalogue
    raise CompatibilityError("official release catalogue exceeded 100 pages")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy-file", type=Path, help="local policy JSON for offline validation")
    parser.add_argument("--releases-file", type=Path, help="local releases API JSON for offline validation")
    parser.add_argument("--cask", type=Path, default=CASK, help="cask file to update")
    args = parser.parse_args(argv)
    if (args.policy_file is None) != (args.releases_file is None):
        parser.error("--policy-file and --releases-file must be given together")
    try:
        if args.policy_file is None:
            policy, catalogue = fetch_official_data(os.environ.get("GH_TOKEN"))
        else:
            policy = json.loads(args.policy_file.read_text(encoding="utf-8"))
            catalogue = json.loads(args.releases_file.read_text(encoding="utf-8"))
        changed = update_cask(args.cask, policy, catalogue)
        print("Updated cask from official compatibility policy." if changed else "Cask is up to date.")
    except (OSError, json.JSONDecodeError, CompatibilityError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
