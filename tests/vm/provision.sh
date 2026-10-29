#!/bin/sh
# Runs only in the disposable cloud guest, before any KDE transaction is approved.
set -eu
export DEBIAN_FRONTEND=noninteractive
apt-get update
# Start the original desktop only after all session files and autologin exist.
test ! -e /usr/sbin/policy-rc.d && test ! -L /usr/sbin/policy-rc.d
(set -C; printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d)
chmod 0755 /usr/sbin/policy-rc.d
trap 'rm -f /usr/sbin/policy-rc.d' EXIT
apt-get install -y --no-install-recommends qemu-guest-agent python3-apt polkitd pkexec \
    xfce4 lightdm lightdm-gtk-greeter dbus-x11 xvfb imagemagick libglib2.0-bin \
    fonts-dejavu-core x11-utils xserver-xorg-core xserver-xorg-input-libinput xauth x11-xserver-utils
rm /usr/sbin/policy-rc.d
trap - EXIT
# Fixed native dpkg test hook is part of the reviewed baseline; disabled by default.
cat > /usr/local/sbin/udm-ci-dpkg-hook <<'HOOK'
#!/bin/sh
if test -e /run/udm-ci-dpkg-fail; then
    echo 'UDM CI deliberate native dpkg pre-invoke failure' >&2
    exit 42
fi
HOOK
chmod 0755 /usr/local/sbin/udm-ci-dpkg-hook
printf 'pre-invoke=/usr/local/sbin/udm-ci-dpkg-hook\n' > /etc/dpkg/dpkg.cfg.d/udm-ci
printf 'Acquire::Retries "0";\nAcquire::http::Timeout "10";\nAcquire::https::Timeout "10";\n' > /etc/apt/apt.conf.d/99-udm-ci-timeouts
apt-get clean
useradd -m -s /bin/bash desktop
useradd -m -s /bin/bash plasma-check
passwd -l desktop
passwd -l plasma-check
mkdir -p /etc/lightdm/lightdm.conf.d
cat > /etc/lightdm/lightdm.conf.d/90-udm-ci.conf <<'CONF'
[Seat:*]
autologin-user=desktop
autologin-user-timeout=0
user-session=xfce
CONF
# QGA is the only control channel. No SSH keys/passwords/tokens enter snapshots.
systemctl disable --now ssh.service ssh.socket 2>/dev/null || true
python3 - <<'KEYS'
from pathlib import Path
for key in Path('/etc/ssh').glob('ssh_host_*'):
    key.unlink()
KEYS
systemctl disable --now apt-daily.timer apt-daily-upgrade.timer
systemctl mask apt-daily.service apt-daily-upgrade.service
mkdir -p /source
mount -o ro /dev/disk/by-label/UDMSOURCE /source
printf '/dev/disk/by-label/UDMSOURCE /source iso9660 ro 0 0\n' >> /etc/fstab
install -D -o root -g root -m 0755 /source/packaging/debian/udm_packages.py /usr/libexec/udm-packages
install -D -o root -g root -m 0644 /source/packaging/polkit/org.whatzgames.udm.install.policy /usr/share/polkit-1/actions/org.whatzgames.udm.install.policy
install -o root -g root -m 0755 /source/udm-app /usr/local/bin/udm-app
systemctl start qemu-guest-agent
systemctl set-default graphical.target
systemctl start lightdm
# Record provisioning completion separately from graphical readiness.
touch /var/lib/udm-ci-provisioned
