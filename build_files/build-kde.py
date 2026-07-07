#!/usr/bin/python3
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Hadi Chokr <hadichokr@icloud.com>

import os
import subprocess
import logging
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_targets(path="/ctx/targets.txt"):
    with open(path) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


KDE_BUILDER_TARGETS = load_targets()


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

# --- TODO: Hotfix — remove Rust CMake file that conflicts with KDE's Rust builds ---
subprocess.run(["dnf5", "install", "-y", "qt6-qtwebengine-devel"])
rust_cmake = "/usr/lib64/cmake/Qt6/FindRust.cmake"
if os.path.exists(rust_cmake):
    os.remove(rust_cmake)

# --- Hotfix — remove broken QMobipocket6 CMake config (library missing in rawhide) ---
# The cmake targets file references libQMobipocket6.so.3.0.0 which does not exist,
# causing kfilemetadata to fail to configure. Removing the config lets cmake skip it.
mobipocket_cmake_dir = "/usr/lib64/cmake/QMobipocket6"
if os.path.exists(mobipocket_cmake_dir):
    shutil.rmtree(mobipocket_cmake_dir)

# --- Build ---
os.environ["CXXFLAGS"] = "-ffile-prefix-map=/builder/src/=/usr/src/debug/"

args = ["kde-builder"] + KDE_BUILDER_TARGETS
logger.info(f"Running: {' '.join(args)}")
process = subprocess.run(args=args)
if process.returncode != 0:
    raise Exception(f"kde-builder failed ({process.returncode})")
