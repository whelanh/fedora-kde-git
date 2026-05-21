# ⚙️ fedora-kde-git

An attempt to piggy-back on https://github.com/silverhadch/ublue-kde-dx with the notable change that it substitutes 

`quay.io/fedora-ostree-desktops/base-atomic:rawhide` 

as the base image on which to build the  git master Plasma, KDE Gears and a full KDE development toolchain. 

## Features

- Rawhide base image
- Plasma (git master)
- KDE Gears (git master)
- KDE development tools and dependencies
- Development utilities: `kdevelop`, `flatpak-builder`, `clang`, `neovim`, `zsh`
- Preinstalled `kde-builder` with shell completions
- Enabled system services: `podman.socket`, `NetworkManager`, `bluetooth`, `cups`
---  

### Other departure from `silverhadch/ublue-kde-dx`

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

## Credits

Based on customizations by @silverhadch and the Fedora daily atomic base image.
