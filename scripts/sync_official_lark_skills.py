#!/usr/bin/env python3
"""Sync bundled Lark skills from the official larksuite/cli repository."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


DEFAULT_REPO = "https://github.com/larksuite/cli.git"
DEFAULT_PLUGIN_ROOT = Path(__file__).resolve().parents[1] / "plugins" / "lark"
OVERRIDES_DIR = Path(__file__).resolve().parents[1] / "overrides"


def run(argv: list[str], cwd: Path | None = None) -> str:
    return subprocess.check_output(argv, cwd=cwd, text=True, stderr=subprocess.STDOUT)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin-root", default=str(DEFAULT_PLUGIN_ROOT))
    parser.add_argument("--source", choices=("github", "cli"), default="github")
    parser.add_argument("--official-repo", default=DEFAULT_REPO)
    parser.add_argument("--official-ref", default="main")
    return parser.parse_args()


def copy_official_skills(source_skills: Path, plugin_root: Path) -> list[str]:
    destination = plugin_root / "skills"
    destination.mkdir(parents=True, exist_ok=True)

    for child in destination.iterdir():
        if child.is_dir() and child.name.startswith("lark-"):
            shutil.rmtree(child)

    copied: list[str] = []
    for child in sorted(source_skills.iterdir(), key=lambda item: item.name):
        if child.is_dir() and child.name.startswith("lark-"):
            shutil.copytree(child, destination / child.name)
            copied.append(child.name)
    return copied


def apply_local_overrides(plugin_root: Path) -> list[str]:
    """Apply repository-owned overrides after replacing the official skills tree.

    The auth-refresh guidance is kept as a standalone reference and only adds a
    small discovery hook to the upstream skill. This avoids a large contextual
    patch breaking whenever upstream reorganizes otherwise unrelated content.
    Any remaining patches deliberately use contextual hunks so an actual
    semantic overlap still stops the sync.
    """
    if plugin_root != DEFAULT_PLUGIN_ROOT.resolve() or not OVERRIDES_DIR.exists():
        return []

    applied: list[str] = []

    auth_refresh_override = OVERRIDES_DIR / "lark-shared-auth-refresh.md"
    if auth_refresh_override.exists():
        shared_skill = plugin_root / "skills" / "lark-shared"
        shared_skill_file = shared_skill / "SKILL.md"
        shared_reference = shared_skill / "references" / auth_refresh_override.name

        lines = shared_skill_file.read_text(encoding="utf-8").splitlines(keepends=True)
        frontmatter_boundaries = [index for index, line in enumerate(lines) if line.rstrip() == "---"]
        if len(frontmatter_boundaries) < 2:
            raise RuntimeError(f"Missing YAML frontmatter in {shared_skill_file}")

        description_indexes = [
            index
            for index in range(frontmatter_boundaries[0] + 1, frontmatter_boundaries[1])
            if lines[index].startswith("description:")
        ]
        if len(description_indexes) != 1:
            raise RuntimeError(f"Expected one description in {shared_skill_file}")
        lines[description_indexes[0]] = (
            'description: "Use for lark-cli setup/auth tasks: first-time app configuration '
            "versus existing-app user reauthorization, expired refresh tokens, auth "
            "login/status/logout, user vs bot identity, business-domain permissions "
            "(--domain, including all/docs/drive), missing scopes, revoking authorization, "
            'or handling _notice JSON."\n'
        )

        refresh_trigger = (
            "| refresh token 过期、已有应用重新授权、区分首次配置与重新登录 | "
            "[`lark-shared-auth-refresh.md`](references/lark-shared-auth-refresh.md) |\n"
        )
        if refresh_trigger not in lines:
            identity_rows = [
                index
                for index, line in enumerate(lines)
                if line.startswith("|") and "lark-shared-identity-and-permissions.md" in line
            ]
            if len(identity_rows) != 1:
                raise RuntimeError(
                    f"Expected one identity-and-permissions trigger row in {shared_skill_file}"
                )
            lines.insert(identity_rows[0], refresh_trigger)

        shared_skill_file.write_text("".join(lines), encoding="utf-8")
        shared_reference.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(auth_refresh_override, shared_reference)
        applied.append(auth_refresh_override.name)

    for patch in sorted(OVERRIDES_DIR.glob("*.patch")):
        run(["git", "apply", "--check", str(patch)], cwd=repo_root())
        run(["git", "apply", str(patch)], cwd=repo_root())
        applied.append(patch.name)
    return applied


def sync_from_github(args: argparse.Namespace, plugin_root: Path) -> dict[str, str | int | list[str]]:
    with tempfile.TemporaryDirectory(prefix="lark-cli-sync-") as tmp:
        checkout = Path(tmp) / "cli"
        run(["git", "clone", "--depth", "1", args.official_repo, str(checkout)])
        run(["git", "checkout", args.official_ref], cwd=checkout)

        commit = run(["git", "rev-parse", "HEAD"], cwd=checkout).strip()
        package = json.loads((checkout / "package.json").read_text(encoding="utf-8"))
        copied = copy_official_skills(checkout / "skills", plugin_root)

        notices = repo_root() / "THIRD_PARTY_NOTICES"
        notices.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(checkout / "LICENSE", notices / "larksuite-cli-LICENSE")

        return {
            "source": "github",
            "source_repo": args.official_repo,
            "source_ref": args.official_ref,
            "source_commit": commit,
            "package_version": package["version"],
            "skill_count": len(copied),
            "skills": copied,
        }


def list_cli_entries(path: str | None = None) -> dict:
    argv = ["lark-cli", "skills", "list"]
    if path:
        argv.append(path)
    return json.loads(run(argv))


def read_cli_file(path: str) -> str:
    return run(["lark-cli", "skills", "read", path])


def export_cli_path(path: str, destination_root: Path) -> None:
    payload = list_cli_entries(path)
    for entry in payload.get("entries", []):
        entry_path = entry["path"]
        output_path = destination_root / entry_path
        if entry["is_dir"]:
            output_path.mkdir(parents=True, exist_ok=True)
            export_cli_path(entry_path, destination_root)
        else:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(read_cli_file(entry_path), encoding="utf-8")


def sync_from_cli(plugin_root: Path) -> dict[str, str | int | list[str]]:
    payload = list_cli_entries()
    skills = [item["name"] for item in payload.get("skills", []) if item["name"].startswith("lark-")]
    destination = plugin_root / "skills"
    destination.mkdir(parents=True, exist_ok=True)

    for child in destination.iterdir():
        if child.is_dir() and child.name.startswith("lark-"):
            shutil.rmtree(child)

    for skill in skills:
        export_cli_path(skill, destination)

    version = run(["lark-cli", "--version"]).strip().split()[-1]
    return {
        "source": "cli",
        "source_repo": DEFAULT_REPO,
        "source_ref": "installed-cli",
        "source_commit": "embedded",
        "package_version": version,
        "skill_count": len(skills),
        "skills": skills,
    }


def update_manifest(plugin_root: Path, metadata: dict[str, str | int | list[str]]) -> None:
    manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    package_version = str(metadata["package_version"]).split("+", 1)[0]
    commit = str(metadata["source_commit"])
    build = commit[:12] if commit != "embedded" else "embedded"
    manifest["version"] = f"{package_version}+official.{build}"
    manifest["description"] = "Codex plugin wrapper for official Lark/Feishu lark-cli skills."
    manifest.setdefault("author", {})["name"] = "chang-xinhai"
    manifest["homepage"] = "https://github.com/chang-xinhai/lark-codex-plugin"
    manifest["repository"] = "https://github.com/chang-xinhai/lark-codex-plugin"
    manifest["license"] = "MIT"
    manifest["keywords"] = ["lark", "feishu", "codex", "lark-cli", "skills"]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_sync_metadata(metadata: dict[str, str | int | list[str]]) -> None:
    payload = dict(metadata)
    target = repo_root() / "THIRD_PARTY_NOTICES" / "larksuite-cli-source.json"
    if target.exists():
        previous = json.loads(target.read_text(encoding="utf-8"))
        previous_without_time = {key: value for key, value in previous.items() if key != "synced_at_utc"}
        if previous_without_time == payload:
            payload["synced_at_utc"] = previous.get("synced_at_utc")
        else:
            payload["synced_at_utc"] = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    else:
        payload["synced_at_utc"] = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    plugin_root = Path(args.plugin_root).resolve()
    if args.source == "github":
        metadata = sync_from_github(args, plugin_root)
    else:
        metadata = sync_from_cli(plugin_root)
    overrides = apply_local_overrides(plugin_root)
    update_manifest(plugin_root, metadata)
    write_sync_metadata(metadata)
    print(
        f"Synced {metadata['skill_count']} skills from {metadata['source']} "
        f"({metadata['package_version']} {metadata['source_commit']}); "
        f"applied {len(overrides)} local override(s)."
    )


if __name__ == "__main__":
    main()
