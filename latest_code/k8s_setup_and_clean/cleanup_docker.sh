#!/bin/bash
set -euo pipefail
trap 'echo "Error on line $LINENO."' ERR

echo "Stopping Docker..."
systemctl stop docker || true
systemctl stop docker.socket || true

echo "Removing Docker packages..."
apt-get purge -y docker-ce docker-ce-cli docker-compose-plugin containerd.io docker-buildx-plugin docker-ce-rootless-extras
apt-get autoremove -y
apt-get autoclean

echo "Removing all Docker data and configs..."
rm -rf /var/lib/docker
rm -rf /var/lib/containerd
rm -rf /etc/docker
rm -rf ~/.docker
rm -rf /run/docker*

echo "Removing leftover binaries..."
rm -f /usr/bin/docker /usr/bin/dockerd
rm -f /usr/local/bin/docker /usr/local/bin/docker-compose
rm -f /lib/systemd/system/docker.service
rm -f /lib/systemd/system/docker.socket

echo "Reloading systemd..."
systemctl daemon-reexec
systemctl daemon-reload

echo "Docker cleanup complete!"
