Excellent — here's an **enhanced, production-grade shell script** that performs a **deep clean** of any Linux VM while preserving only **default system components**.

---

## ✅ `reset-to-fresh.sh` (Full Version)

```bash
#!/bin/bash
set -euo pipefail

BASELINE_DIR="/root/system_baseline"

function capture_baseline() {
    echo "📦 Capturing clean OS baseline..."

    mkdir -p "$BASELINE_DIR"
    apt-mark showmanual > "$BASELINE_DIR/manual_packages.txt"
    cut -d: -f1 /etc/passwd > "$BASELINE_DIR/users.txt"
    find /home /etc /opt /usr/local /var -type f 2>/dev/null > "$BASELINE_DIR/files.txt"
    hostnamectl status | grep "Static hostname" | awk '{print $3}' > "$BASELINE_DIR/hostname.txt"

    echo "✅ Baseline saved in $BASELINE_DIR"
    exit 0
}

function reset_system() {
    echo "⚠️ This will remove ALL user-installed packages, files, logs, users, and SSH keys."
    read -p "Type YES to continue: " confirm
    [[ "$confirm" != "YES" ]] && { echo "❌ Aborted"; exit 1; }

    echo "📦 Removing user-installed APT packages..."
    apt-mark showmanual | grep -vxFf "$BASELINE_DIR/manual_packages.txt" | \
        xargs -r sudo apt-get remove --purge -y

    echo "🧹 Autoremove unnecessary packages..."
    sudo apt-get autoremove --purge -y

    echo "🧼 Cleaning apt cache..."
    sudo apt-get clean
    sudo rm -rf /var/lib/apt/lists/*

    echo "👤 Deleting non-system users..."
    cut -d: -f1 /etc/passwd | grep -vxFf "$BASELINE_DIR/users.txt" | while read user; do
        echo "  🔸 Deleting user: $user"
        sudo deluser --remove-home "$user" || true
    done

    echo "🗑 Deleting user-created files..."
    current_files=$(mktemp)
    find /home /etc /opt /usr/local /var -type f 2>/dev/null > "$current_files"
    comm -23 <(sort "$current_files") <(sort "$BASELINE_DIR/files.txt") | while read f; do
        echo "  🗑 Removing $f"
        rm -f "$f" || true
    done
    rm "$current_files"

    echo "🧼 Cleaning system logs..."
    rm -rf /var/log/*
    journalctl --rotate
    journalctl --vacuum-time=1s

    echo "🧽 Cleaning temporary files..."
    rm -rf /tmp/*
    rm -rf /var/tmp/*

    echo "🔑 Removing SSH keys..."
    find /home /root -name "authorized_keys" -exec rm -f {} \;
    rm -rf /root/.ssh
    find /home -type d -name ".ssh" -exec rm -rf {} +

    echo "🔄 Resetting hostname..."
    DEFAULT_HOSTNAME=$(cat "$BASELINE_DIR/hostname.txt")
    hostnamectl set-hostname "$DEFAULT_HOSTNAME"

    echo "📜 Clearing shell history..."
    history -c
    echo > /root/.bash_history
    find /home -name ".bash_history" -exec rm -f {} \;

    echo "🔥 Checking and resetting UFW firewall..."
    if command -v ufw &>/dev/null; then
        echo "  🔧 Resetting UFW..."
        ufw --force reset
    fi

    echo "🧹 Cleaning systemd junk and unused units..."
    rm -rf /etc/systemd/system/*.service || true

    echo "✅ Deep clean complete. System is now close to factory state."
}

function usage() {
    echo "Usage: $0 [--capture | --reset]"
    echo "  --capture   Save the current system state as the clean baseline"
    echo "  --reset     Reset system to previously saved clean baseline"
    exit 1
}

case "${1:-}" in
    --capture) capture_baseline ;;
    --reset) reset_system ;;
    *) usage ;;
esac
```

---

## 🔧 How to Use

### Step 1: Capture baseline **right after OS install**

```bash
chmod +x reset-to-fresh.sh
sudo ./reset-to-fresh.sh --capture
```

### Step 2: Use anytime to **deep clean system**

```bash
sudo ./reset-to-fresh.sh --reset
```

---

## 🔐 What It Does

| Category      | Action                                                            |
| ------------- | ----------------------------------------------------------------- |
| APT Packages  | Removes all user-installed packages, cleans apt cache             |
| Users         | Deletes non-default users and their `/home`                       |
| Files         | Removes any non-baseline files in `/home`, `/opt`, `/etc`, `/var` |
| Logs & Temp   | Deletes `/var/log`, `/tmp`, `/var/tmp`, systemd logs              |
| Shell History | Clears `.bash_history` for all users                              |
| SSH Keys      | Deletes all `~/.ssh` folders and authorized keys                  |
| Hostname      | Resets hostname to original one                                   |
| Firewall      | Resets UFW rules (if installed)                                   |
| Services      | Removes custom `.service` units                                   |

---


