FROM debian:13
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    kwin-wayland plasma-desktop plasma-workspace plasma-integration breeze dbus-x11 libglib2.0-bin \
    xvfb libgl1-mesa-dri libegl-mesa0 imagemagick python3 fonts-dejavu-core libcap2-bin \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 smoke \
    && install -d -o smoke -g smoke /tmp/plasma-artifacts
# The realtime file capability prevents exec inside Docker's default capability bound.
RUN getcap /usr/bin/kwin_wayland && setcap -r /usr/bin/kwin_wayland \
    && install -d -m 1777 /tmp/.X11-unix
COPY smoke.py /opt/plasma-smoke.py
USER smoke
ENV HOME=/home/smoke LANG=C.UTF-8
ENTRYPOINT ["dbus-run-session", "--", "python3", "/opt/plasma-smoke.py"]
