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

### Departure from `silverhadch/fedora-plasma-canary`

For my own purposes, the build_files/boostrap.sh also includes: 

`gcc gcc-c++ gcc-gfortran make fastfetch htop duf cmake git gh fuse 
    fprintd fprintd-pam tcl-devel tk-devel python-pyqt6 python-pyqt6-webengine 
    edk2-ovmf libvirt libvirt-nss PackageKit docker distrobox podman-compose 
    podman-machine qemu-char-spice qemu-device-display-virtio-gpu 
    qemu-device-display-virtio-vga qemu-device-usb-redirect qemu-img 
    qemu-system-x86-core qemu-user-binfmt qemu-user-static qemu virt-manager tailscale
    fuse fuse-libs`

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

