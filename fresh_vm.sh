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




#################################################################



#!/bin/bash
set -euo pipefail

BASELINE_DIR="/root/system_baseline"
BACKUP_DIR="/root/user_backup_$(date +%Y%m%d_%H%M%S)"
DRY_RUN=false

function capture_baseline() {
    echo "\n📦 Capturing clean OS baseline..."
    mkdir -p "$BASELINE_DIR"

    apt-mark showmanual > "$BASELINE_DIR/manual_packages.txt"
    cut -d: -f1 /etc/passwd > "$BASELINE_DIR/users.txt"
    find /etc /usr/local /var -type f 2>/dev/null > "$BASELINE_DIR/files.txt"
    hostnamectl status | grep "Static hostname" | awk '{print $3}' > "$BASELINE_DIR/hostname.txt"

    echo "✅ Baseline saved in $BASELINE_DIR"
    exit 0
}

function backup_user_data() {
    echo "\n🧾 Backing up user-installed data to $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"

    apt-mark showmanual > "$BACKUP_DIR/manual_packages_backup.txt"
    dpkg --get-selections > "$BACKUP_DIR/dpkg_selection.txt"

    cut -d: -f1 /etc/passwd | grep -vxFf "$BASELINE_DIR/users.txt" | while read user; do
        HOME_DIR=$(eval echo "~$user")
        if [ -d "$HOME_DIR" ]; then
            echo "  🔸 Backing up $user home ($HOME_DIR)"
            tar czf "$BACKUP_DIR/${user}_home_backup.tar.gz" "$HOME_DIR"
        fi
    done

    cp -a /root/.ssh "$BACKUP_DIR/root_ssh" 2>/dev/null || true
    cp -a /etc/systemd/system/*.service "$BACKUP_DIR/systemd_services/" 2>/dev/null || true
    cp -a /var/log "$BACKUP_DIR/logs/"
    cp -a /etc "$BACKUP_DIR/etc_snapshot/"
}

function reset_system() {
    echo "\n⚠️ This will RESET your system to a clean state."
    read -p "Type YES to create a backup and continue: " confirm
    [[ "$confirm" != "YES" ]] && { echo "❌ Aborted"; exit 1; }

    backup_user_data

    echo "\n📦 Checking for user-installed APT packages..."
    comm -23 <(sort <(apt-mark showmanual)) <(sort "$BASELINE_DIR/manual_packages.txt") > /tmp/user_apt_packages.txt
    if $DRY_RUN; then
        echo "Would remove APT packages:"; cat /tmp/user_apt_packages.txt
    else
        xargs -r sudo apt-get remove --purge -y < /tmp/user_apt_packages.txt
        sudo apt-get autoremove --purge -y
        sudo apt-get clean
        sudo rm -rf /var/lib/apt/lists/*
    fi

    echo "\n👤 Checking for non-system users..."
    cut -d: -f1 /etc/passwd | grep -vxFf "$BASELINE_DIR/users.txt" > /tmp/custom_users.txt
    if $DRY_RUN; then
        echo "Would delete users:"; cat /tmp/custom_users.txt
    else
        while read user; do
            sudo deluser --remove-home "$user" || true
        done < /tmp/custom_users.txt
    fi

    echo "\n🗑 Comparing and checking for extra files..."
    find /etc /usr/local /var -type f 2>/dev/null > /tmp/current_files.txt
    comm -23 <(sort /tmp/current_files.txt) <(sort "$BASELINE_DIR/files.txt") > /tmp/extra_files.txt
    if $DRY_RUN; then
        echo "Would delete files:"; cat /tmp/extra_files.txt
    else
        while read f; do rm -f "$f" || true; done < /tmp/extra_files.txt
    fi

    echo "\n🧼 Cleaning logs, temp, and systemd junk..."
    if ! $DRY_RUN; then
        rm -rf /var/log/*
        journalctl --rotate
        journalctl --vacuum-time=1s
        rm -rf /tmp/*
        rm -rf /var/tmp/*
    fi

    echo "\n🔑 Checking SSH key removal..."
    if $DRY_RUN; then
        find /home /root -name "authorized_keys"
    else
        find /home /root -name "authorized_keys" -exec rm -f {} \;
        rm -rf /root/.ssh
        find /home -type d -name ".ssh" -exec rm -rf {} +
    fi

    echo "\n🔄 Hostname reset..."
    DEFAULT_HOSTNAME=$(cat "$BASELINE_DIR/hostname.txt")
    if $DRY_RUN; then
        echo "Would set hostname to $DEFAULT_HOSTNAME"
    else
        hostnamectl set-hostname "$DEFAULT_HOSTNAME"
    fi

    echo "\n📜 Clearing shell history..."
    if $DRY_RUN; then
        echo "Would clear bash histories"
    else
        history -c
        echo > /root/.bash_history
        find /home -name ".bash_history" -exec rm -f {} \;
    fi

    echo "\n🔥 Checking UFW firewall reset..."
    if command -v ufw &>/dev/null; then
        if $DRY_RUN; then
            echo "Would reset UFW firewall"
        else
            ufw --force reset
        fi
    fi

    echo "\n✅ Dry run complete. Nothing has been deleted." && $DRY_RUN && exit 0
    echo "✅ System has been reset. Backup is in: $BACKUP_DIR"
}

function usage() {
    echo "Usage: $0 [--capture | --reset | --dry-run]"
    echo "  --capture     Save clean system baseline (run after OS install)"
    echo "  --reset       Backup and clean system to match baseline"
    echo "  --dry-run     Preview changes without deleting"
    exit 1
}

case "${1:-}" in
    --capture) capture_baseline ;;
    --reset) reset_system ;;
    --dry-run) DRY_RUN=true; reset_system ;;
    *) usage ;;
esac


