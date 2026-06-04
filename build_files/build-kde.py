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
    "ark",
    "audiocd-kio",
    "auto-chmod",
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

subprocess.run(["dnf5", "install", "-y", "ibus-devel"], check=True)

# Symlink ibus-visibility.h into the main ibus include dir.
# ibusversion.h includes <ibus-visibility.h> but the file lives in
# /usr/lib64/ibus-1.0/include/ which is not on the default search path.
ibus_vis = "/usr/lib64/ibus-1.0/include/ibus-visibility.h"
ibus_inc = "/usr/include/ibus-1.0/ibus-visibility.h"
if os.path.exists(ibus_vis) and not os.path.exists(ibus_inc):
    os.symlink(ibus_vis, ibus_inc)
    logger.info("Symlinked ibus-visibility.h into /usr/include/ibus-1.0/")
else:
    logger.warning(f"ibus-visibility.h fixup skipped (src={os.path.exists(ibus_vis)}, dst_exists={os.path.exists(ibus_inc)})")

# --- Build ---
os.environ["CXXFLAGS"] = "-ffile-prefix-map=/builder/src/=/usr/src/debug/"

args = ["kde-builder", "--refresh-build"] + KDE_BUILDER_TARGETS
logger.info(f"Running: {' '.join(args)}")
process = subprocess.run(args=args)
if process.returncode != 0:
    raise Exception(f"kde-builder failed ({process.returncode})")
