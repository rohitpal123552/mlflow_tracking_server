#!/bin/bash

set -euo pipefail
trap 'echo "Error on line $LINENO. Exiting."' ERR

K8S_VERSION="1.32.1"
POD_CIDR="192.168.0.0/16"

echo "[1/7] Disabling swap..."
swapoff -a
sed -i '/ swap / s/^/#/' /etc/fstab

echo "[2/7] Installing prerequisites..."
apt-get update -y
apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release software-properties-common

echo "[3/7] Setting kernel parameters..."
cat <<EOF | tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

modprobe overlay
modprobe br_netfilter

cat <<EOF | tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

sysctl --system

echo "[4/7] Installing containerd..."
apt-get install -y containerd
mkdir -p /etc/containerd
containerd config default | tee /etc/containerd/config.toml
sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
systemctl restart containerd
systemctl enable containerd

echo "[5/7] Installing Kubernetes $K8S_VERSION components..."
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.32/deb/Release.key | gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.32/deb/ /" > /etc/apt/sources.list.d/kubernetes.list
apt-get update
apt-get install -y kubelet=${K8S_VERSION}-1.1 kubeadm=${K8S_VERSION}-1.1 kubectl=${K8S_VERSION}-1.1
apt-mark hold kubelet kubeadm kubectl

echo "[6/7] Initializing Kubernetes control plane..."
kubeadm init --kubernetes-version=${K8S_VERSION} --pod-network-cidr=${POD_CIDR} --ignore-preflight-errors=NumCPU

echo "[7/7] Configuring kubectl access..."
mkdir -p $HOME/.kube
cp /etc/kubernetes/admin.conf $HOME/.kube/config
chown $(id -u):$(id -g) $HOME/.kube/config

echo "Installing Calico CNI..."
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.27.0/manifests/calico.yaml

echo "Wait for 1 mins"
sleep 60

echo "Allowing pod scheduling on control-plane (for single-node cluster)..."
kubectl taint nodes --all node-role.kubernetes.io/control-plane- || true

echo "Kubernetes v${K8S_VERSION} setup complete!"
kubectl get nodes -o wide
