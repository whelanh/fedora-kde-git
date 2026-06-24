#!/usr/bin/python3
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Hadi Chokr <hadichokr@icloud.com>

import os
import subprocess
import logging
import shutil
import time
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KDE_BUILDER_TARGETS = [
    "ark",
    "audiocd-kio",
    "auto-chmod",
    "discover",
    "dolphin",
    "dolphin-plugins",
    "ffmpegthumbs",
    "kdeconnect-kde",
    "kdegraphics-thumbnailers",
    "kde-inotify-survey",
    "kdenetwork-filesharing",
    "kdialog",
    "kimageformats",
    "kio-admin",
    "kio-fuse",
    "kio-gdrive",
    "plasma-setup",
    "plasma-wayland-protocols",
    "kapsule",
    "konlineaccounts",
    "konsole",
    "kpmcore",
    "kunifiedpush",
    "kup",
    "kwalletmanager",
    "package-compatibility-helper",
    "partitionmanager",
    "pulseaudio-qt",
    "selenium-webdriver-at-spi",
    "spectacle",
    "workspace",
    "xwaylandvideobridge",
]


def run_kde_builder(args):
    args = ["kde-builder"] + args
    logger.info(f"Running: {' '.join(args)}")
    process = subprocess.run(args=args, capture_output=True, text=True)
    if process.returncode != 0:
        raise Exception(
            f"kde-builder failed ({process.returncode}): {process.stdout}"
        )
    return process.stdout


# --- ccache ---
os.environ["CCACHE_DIR"] = "/ccache"

# --- Setup config ---
config_dir = "/root/.config"
os.makedirs(config_dir, exist_ok=True)
shutil.copy("/ctx/kde-builder.yaml", f"{config_dir}/kde-builder.yaml")

# Pre-clone sysadmin/repo-metadata so kde-builder finds the directory already present.
# kde-builder's _verify_ref_present() runs `git ls-remote` with a 10-second Python timeout
# before cloning, which can be hit on slow or congested networks. When the directory already
# exists, kde-builder calls update_existing_clone() (uses `git fetch`, no short timeout) and
# skips the ls-remote check entirely.
_metadata_state_home = os.environ.get("XDG_STATE_HOME") or os.path.join(os.environ["HOME"], ".local/state")
_metadata_dir = os.path.join(_metadata_state_home, "sysadmin-repo-metadata")
if not os.path.exists(os.path.join(_metadata_dir, ".git")):
    os.makedirs(_metadata_state_home, exist_ok=True)
    logger.info("Pre-cloning sysadmin/repo-metadata to bypass kde-builder ls-remote timeout...")
    _cloned = False
    for _attempt in range(5):
        if _attempt > 0:
            if os.path.exists(_metadata_dir):
                shutil.rmtree(_metadata_dir)
            time.sleep(5)
        if subprocess.run(
            ["git", "clone", "https://invent.kde.org/sysadmin/repo-metadata.git", _metadata_dir],
            capture_output=True,
        ).returncode == 0:
            _cloned = True
            break
        logger.warning(f"repo-metadata pre-clone attempt {_attempt + 1}/5 failed, retrying...")
    if _cloned:
        # kde-builder hardcodes branch='master' for repo-metadata. If the remote's
        # default branch is something else (e.g. 'main'), set up origin/master so
        # kde-builder can check it out successfully.
        _head = subprocess.run(
            ["git", "-C", _metadata_dir, "branch", "--show-current"],
            capture_output=True, text=True,
        ).stdout.strip()
        if _head and _head != "master":
            logger.info(f"Remote default branch is '{_head}'; mapping it to 'master' for kde-builder...")
            subprocess.run(
                ["git", "-C", _metadata_dir, "config", "remote.origin.fetch",
                 f"+refs/heads/{_head}:refs/remotes/origin/master"],
                check=True,
            )
            subprocess.run(["git", "-C", _metadata_dir, "fetch", "origin"], capture_output=True)
            subprocess.run(
                ["git", "-C", _metadata_dir, "checkout", "-b", "master", "origin/master"],
                capture_output=True,
            )
        logger.info("repo-metadata pre-clone succeeded")
    else:
        logger.warning("All pre-clone attempts failed; kde-builder will attempt it directly (may timeout)")

run_kde_builder(["--metadata-only"])

# Required dependency for webengine consumers
subprocess.run(["dnf5", "install", "-y", "qt6-qtwebengine-devel"], check=True)

# Remove ibus-devel: the rawhide container environment has a broken
# ibus-visibility.h include chain that causes plasma-desktop's kimpanel
# ibus backend to fail to compile.  ibus-devel is pulled in by
# install-kde-deps.py (fedora.yaml), so we must actively remove it.
# Without it, CMake simply skips the ibus backend.  The SCIM backend
# and the rest of plasma-desktop are unaffected.
subprocess.run(["dnf5", "remove", "-y", "ibus-devel"], check=False)

# --- Source Update and Patching ---
logger.info("Updating sources...")
run_kde_builder(["--src-only"] + KDE_BUILDER_TARGETS)

updates_cpp_path = "/builder/src/discover/kcm/updates.cpp"
if os.path.exists(updates_cpp_path):
    logger.info(f"Patching {updates_cpp_path} to include <QQmlEngine> and <QtQml>...")
    with open(updates_cpp_path, "r") as f:
        content = f.read()
    if "#include <QQmlEngine>" not in content:
        patched_content = "#include <QQmlEngine>\n#include <QtQml>\n" + content
        with open(updates_cpp_path, "w") as f:
            f.write(patched_content)
        logger.info("Successfully patched updates.cpp")
    else:
        logger.info("updates.cpp already contains <QQmlEngine>")
else:
    logger.warning(f"Could not find {updates_cpp_path} to patch!")

# --- Build ---
os.environ["CXXFLAGS"] = "-ffile-prefix-map=/builder/src/=/usr/src/debug/"

args = ["kde-builder", "--no-src", "--refresh-build"] + KDE_BUILDER_TARGETS
logger.info(f"Running: {' '.join(args)}")
process = subprocess.run(args=args)
if process.returncode != 0:
    raise Exception(f"kde-builder failed ({process.returncode})")
