# ⚙️ fedora-kde-git

An attempt to piggy-back on https://github.com/silverhadch/ublue-kde-dx with the notable change that it substitutes quay.io/fedora-ostree-desktops/base-atomic:rawhide as the base image on which to build the  git master Plasma and KDE Gears and a full KDE development toolchain. 

## Features

- Rawhide base image
- Plasma (git master)
- KDE Gears (git master)
- KDE development tools and dependencies
- Development utilities: `kdevelop`, `flatpak-builder`, `clang`, `neovim`, `zsh`
- Preinstalled `kde-builder` with shell completions
- Enabled system services: `podman.socket`, `NetworkManager`, `bluetooth`, `cups`, and more

## Images

> [!WARNING]
> **`-dev` images are experimental and will be broken.**
> They are built from the `dev` branch and may fail to boot or produce a broken desktop at any time. Do not use them.

## Rebase to This Image

### Regular (AMD/Intel)

```bash
sudo rpm-ostree rebase ostree-unverified-registry:ghcr.io/silverhadch/ublue-kde-dx:latest
```

### NVIDIA

```bash
sudo rpm-ostree rebase ostree-unverified-registry:ghcr.io/silverhadch/ublue-kde-dx-nvidia:latest
```

Reboot afterwards to apply the image.

## Credits

Based on dustomizations by @silverhadch and the Fedora project.
