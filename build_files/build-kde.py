#!/usr/bin/python3
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Hadi Chokr <hadichokr@icloud.com>

import os
import subprocess
import logging
import shutil
from pathlib import Path

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


def latest_log_dir(log_root="/builder/log"):
    root = Path(log_root)
    if not root.exists():
        return None

    log_dirs = [path for path in root.iterdir() if path.is_dir()]
    if not log_dirs:
        return None

    return max(log_dirs, key=lambda path: path.stat().st_mtime)


def failed_update_modules():
    log_dir = latest_log_dir()
    if log_dir is None:
        return []

    failed_updates = log_dir / "failed-to-update.log"
    if not failed_updates.exists():
        return []

    with open(failed_updates) as f:
        return [line.strip() for line in f if line.strip()]


def clear_cached_project(module):
    removed = []
    for root in (Path("/builder/src"), Path("/builder/build")):
        if not root.exists():
            continue

        candidate_paths = [root / module]
        candidate_paths.extend(path / module for path in root.iterdir() if path.is_dir())

        for path in candidate_paths:
            if not path.is_dir():
                continue
            shutil.rmtree(path)
            removed.append(str(path))

    if removed:
        logger.warning(f"Removed cached paths for {module}: {', '.join(removed)}")

    return bool(removed)


def build_kde():
    args = ["kde-builder"] + KDE_BUILDER_TARGETS
    logger.info(f"Running: {' '.join(args)}")
    return subprocess.run(args=args).returncode


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

build_exit = build_kde()
if build_exit != 0:
    retried_modules = [module for module in failed_update_modules() if clear_cached_project(module)]
    if not retried_modules:
        raise Exception(f"kde-builder failed ({build_exit})")

    logger.warning(
        f"Retrying kde-builder after clearing failed update modules: {', '.join(retried_modules)}"
    )
    build_exit = build_kde()
    if build_exit != 0:
        raise Exception(f"kde-builder failed ({build_exit})")
