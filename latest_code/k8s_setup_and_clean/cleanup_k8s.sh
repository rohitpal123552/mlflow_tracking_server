#!/bin/bash

set -euo pipefail
trap 'echo "Error on line $LINENO."' ERR

echo "Stopping Kubernetes services..."
systemctl stop kubelet 
systemctl stop containerd 

echo "Resetting kubeadm..."
kubeadm reset -f

echo "Cleaning CNI config, iptables, and kube config..."
rm -rf /etc/cni /opt/cni /var/lib/cni
iptables -F
iptables -t nat -F
iptables -t mangle -F
iptables -X

rm -rf ~/.kube

echo "Removing Kubernetes packages and configs..."
apt-mark unhold kubeadm kubelet kubectl || true
apt-get purge -y --allow-change-held-packages kubeadm kubelet kubectl kubernetes-cni cri-tools containerd
apt-get autoremove -y
apt-get autoclean

rm -rf ~/.kube
rm -rf /etc/kubernetes
rm -rf /var/lib/etcd
rm -rf /var/lib/kubelet
rm -rf /etc/cni /opt/cni /var/lib/cni
rm -rf /etc/containerd /var/lib/containerd

echo "Removing leftover binaries..."
rm -f /usr/bin/kubeadm /usr/bin/kubelet /usr/bin/kubectl
rm -f /usr/local/bin/kubeadm /usr/local/bin/kubectl /usr/local/bin/kubelet
rm -f /etc/systemd/system/kubelet.service.d/10-kubeadm.conf

echo "Reloading systemd..."
systemctl daemon-reexec
systemctl daemon-reload

echo "Kubernetes and containerd cleanup complete!"
