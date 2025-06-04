#!/bin/bash
set -euo pipefail
trap 'echo "Error on line $LINENO."' ERR

DOCKER_VERSION="5:28.1.1-1~ubuntu.22.04~jammy" 

echo "Removing any old Docker versions..."
sudo apt-get remove -y docker docker-engine docker.io containerd runc || true

echo "Installing required packages..."
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release

echo "Adding Docker’s official GPG key..."
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo "Setting up Docker repository..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "Updating APT with Docker repo..."
sudo apt-get update

echo "Installing Docker v$DOCKER_VERSION..."
sudo apt-get install -y docker-ce=${DOCKER_VERSION} docker-ce-cli=${DOCKER_VERSION} containerd.io docker-buildx-plugin docker-compose-plugin

echo "Enabling Docker service..."
sudo systemctl enable docker
sudo systemctl start docker

echo "Testing Docker installation..."
sudo docker version
sudo docker run hello-world

echo "Docker v28.1.1 installed successfully!"
