# ⚙️ ublue-kde-dx

A Kinoite Image with git master Plasma and Gears plus full KDE development tools. Perfect for KDE developers.

## Features

- Plasma (git master)
- KDE Gears (git master)
- KDE development tools and dependencies
- Development utilities: `kdevelop`, `flatpak-builder`, `clang`, `neovim`, `zsh`
- Preinstalled `kde-builder` with completions
- Enabled system services: `podman.socket`

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

Customizations by @silverhadch. Based on Fedora Kinoite and the Universal Blue Project.
