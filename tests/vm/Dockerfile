FROM debian:13
RUN apt-get update && apt-get dist-upgrade -y \
    && apt-get install -y --no-install-recommends \
    qemu-system-x86 qemu-utils genisoimage ca-certificates curl python3 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /source
ENTRYPOINT ["python3", "tests/vm/run.py"]
