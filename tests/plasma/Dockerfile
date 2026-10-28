FROM debian:13
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    kwin-wayland plasma-desktop plasma-workspace dbus-x11 libglib2.0-bin \
    xvfb libgl1-mesa-dri libegl-mesa0 imagemagick python3-pil fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 smoke \
    && install -d -o smoke -g smoke /tmp/plasma-artifacts
COPY smoke.py /opt/plasma-smoke.py
USER smoke
ENV HOME=/home/smoke
ENTRYPOINT ["dbus-run-session", "--", "python3", "/opt/plasma-smoke.py"]
