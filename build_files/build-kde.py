#!/usr/bin/python3
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Hadi Chokr <hadichokr@icloud.com>

import os
import subprocess
import logging
import shutil
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KDE_BUILDER_TARGETS = [
    "appstream",
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
