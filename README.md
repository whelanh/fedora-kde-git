# ⚙️ fedora-kde-git [![GitHub license](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/whelanh/fedora-kde-git/blob/main/LICENSE) [![Build Status](https://github.com/whelanh/fedora-kde-git/actions/workflows/build.yml/badge.svg)](https://github.com/whelanh/fedora-kde-git/actions/workflows/build.yml) [![CodeQL](https://github.com/whelanh/fedora-kde-git/actions/workflows/dynamic/github-code-scanning/codeql/badge.svg)](https://github.com/whelanh/scidCommunity/actions/workflows/dynamic/github-code-scanning/codeql)

A fork of [https://github.com/silverhadch/fedora-plasma-canary](https://github.com/silverhadch/fedora-plasma-canary) with some additional packages installed (see below).  

## Features

- Rawhide base image
- Plasma (git master)
- KDE Gears (git master)
- KDE development tools and dependencies
- Development utilities: `kdevelop`, `flatpak-builder`, `clang`, `neovim`, `zsh`
- Preinstalled `kde-builder` with shell completions
- Enabled system services: `podman.socket`, `NetworkManager`, `bluetooth`, `cups`
---  

## Fork Departures

This fork diverges from [fedora-plasma-canary](https://github.com/silverhadch/fedora-plasma-canary) in the following ways:

- **Kinoite base image**: switched the base from `fedora-ostree-desktops/base-atomic:rawhide` to `fedora-ostree-desktops/kinoite:rawhide` across the Containerfile, Justfile, and CI workflows.
- **Incremental KDE build caching**: the `kde-build` workflow now caches the kde-builder work directory (source + build objects) and the KDE install tree, and drops `--refresh-build`, so failed builds no longer trigger a full rebuild from scratch.
- **Automatic retry of failed source updates**: `build-kde.py` detects modules listed in `failed-to-update.log`, clears their cached source/build directories, and reruns kde-builder once before giving up.
- **Resilient CI pulls**: the base container image pull now retries up to three times before failing.
- **`stop-on-failure: false`**: kde-builder continues building remaining modules instead of halting on the first failure.
- **QMobipocket6 hotfix**: removes the broken `QMobipocket6` CMake config (references a missing library) to unblock the `kfilemetadata` build on rawhide.
- **Extra build dependency**: installs `highway-devel`, required to build `kquickimageeditor`.
- **Ignore Python build cache artifacts** in `.gitignore`.

---  

## Rebase to This Image

```bash
sudo rpm-ostree rebase ostree-unverified-registry:ghcr.io/whelanh/fedora-kde-git:latest
```

Reboot afterwards to apply the image.

## Justfile recipes

If you have an interest in setting up your own just commands (like Universal Blue's `ujust`), see [https://github.com/whelanh/justfile-recipes](https://github.com/whelanh/justfile-recipes)

## Verification

These images are signed with [Sigstore](https://www.sigstore.dev/)'s [cosign](https://github.com/sigstore/cosign). You can verify the signature by downloading the `cosign.pub` file from this repo and running the following command:

```bash
cosign verify --key cosign.pub ghcr.io/whelanh/fedora-kde-git:latest
```

## 🙏 Gratitude
Based on customizations by @silverhadch and the [Fedora daily atomic](https://quay.io/repository/fedora-ostree-desktops/base-atomic) base image.

