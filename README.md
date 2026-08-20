# Low-Power Private Cloud Server & Immich Photo Backup

A complete, production-ready guide and software bundle to convert a low-power Acer Chromebook (C720/C730 with 2GB RAM) and a Seagate 2TB External Hard Drive into a 24/7 self-hosted private cloud and automatic photo backup server with zero maintenance.

---

## Client Requirements & Architecture Overview

* **Primary Use Case:** Automatic phone photo/video backup from iOS and Android devices anywhere in the world (4G/5G/Wi-Fi), and occasional web access from laptop.
* **Zero Maintenance Guarantee:** 
  * Docker containers with `restart: unless-stopped` auto-start on boot and power recovery.
  * Heavy Machine Learning/AI containers removed to keep idle RAM under 450 MB on 2GB hardware.
  * Pinned container releases to prevent breaking database schema updates.
* **Storage Architecture:**
  * **OS & PostgreSQL Database:** Stored on internal fast SSD (`/var/lib/immich/postgres`) to guarantee database lock stability and high speed.
  * **Photos & 4K Videos:** Stored directly on the Seagate 2TB NTFS Hard Drive (`/mnt/storage/immich_library`).
* **Client Experience:**
  * Clean GNOME Desktop on screen with auto-login.
  * Unified Minimalist Glassmorphic Dashboard showing live CPU temperature, Seagate 2TB SMART health condition, and instant 1-click photo gallery switcher.
  * Easy Wi-Fi management directly from the top notification menu or Cockpit.

---

## Repository Structure

```
├── docker-compose.yml            # Lean Immich deployment (No heavy ML container)
├── .env.example                  # Environment configuration template
├── dashboard_server.py           # Custom Python live server telemetry dashboard
├── systemd/
│   └── server-dashboard.service  # Systemd background service for dashboard
├── autostart/
│   └── dashboard.desktop         # GNOME desktop autostart entry
└── README.md                     # Comprehensive documentation & handover guide
```

---

## Step-by-Step Installation & Setup

### 1. Hardware & BIOS Setup
1. Enable Developer Mode (`Esc + Refresh + Power`, then `Ctrl + D`).
2. Remove the physical Write-Protect (WP) Screw from the Chromebook motherboard.
3. Boot into ChromeOS, open terminal (`Ctrl + Alt + T` -> `shell`), and flash MrChromebox Full ROM UEFI firmware:
   ```bash
   cd; curl -LO mrchromebox.tech/firmware-util.sh
   sudo install -Dt /usr/local/bin -m 755 firmware-util.sh
   sudo firmware-util.sh
   ```
4. Choose **Install/Update UEFI (Full ROM) Firmware**.

### 2. Operating System & Hard Drive Mounting
1. Install **Ubuntu Server (64-bit)** to the internal 16GB drive with OpenSSH enabled.
2. Install the minimal GNOME desktop:
   ```bash
   sudo apt update && sudo apt install -y --no-install-recommends ubuntu-desktop-minimal gdm3 gnome-shell epiphany-browser
   ```
3. Mount the Seagate 2TB NTFS drive with user permissions:
   ```bash
   sudo apt install -y ntfs-3g
   sudo mkdir -p /mnt/storage
   # Add to /etc/fstab for permanent auto-mount:
   echo "UUID=<YOUR-DRIVE-UUID> /mnt/storage ntfs-3g defaults,auto,uid=1000,gid=1000,umask=0022,nofail 0 0" | sudo tee -a /etc/fstab
   sudo mount -a
   ```

### 3. Deploying Immich Photo Cloud
1. Install Docker:
   ```bash
   sudo apt install -y docker.io docker-compose-v2
   sudo systemctl enable --now docker
   sudo usermod -aG docker $USER
   ```
2. Create directories:
   ```bash
   sudo mkdir -p /opt/immich /mnt/storage/immich_library /var/lib/immich/postgres
   sudo chown -R $USER:$USER /opt/immich /mnt/storage/immich_library /var/lib/immich/postgres
   ```
3. Start the containers:
   ```bash
   cd /opt/immich && sudo docker compose up -d
   ```

### 4. Deploying the Unified Glassmorphic Dashboard
1. Copy `dashboard_server.py` to `/home/mepits/dashboard_server.py`.
2. Copy `systemd/server-dashboard.service` to `/etc/systemd/system/server-dashboard.service`.
3. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now server-dashboard.service
   ```

---

## Security & Firewall (UFW) Configuration

Cockpit and SSH are strictly locked to local private subnets to prevent any public exposure:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.0.0/16 to any port 9090 proto tcp comment 'Cockpit Local LAN'
sudo ufw allow from 10.0.0.0/8 to any port 9090 proto tcp comment 'Cockpit Local LAN'
sudo ufw allow from 192.168.0.0/16 to any port 2283 proto tcp comment 'Immich Local LAN'
sudo ufw allow from 192.168.0.0/16 to any port 22 proto tcp comment 'SSH Local LAN'
sudo ufw allow in on tailscale0 to any port 22 proto tcp comment 'SSH Tailscale Admin'
sudo ufw enable
```

---

## How to Access and Upload from Anywhere (Outside Home / 4G / 5G)

### Option A: Cloudflare Tunnel (Recommended - Zero Client Friction)
1. On your server, install Cloudflare Tunnel:
   ```bash
   curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
   sudo dpkg -i cloudflared.deb
   ```
2. Route a public hostname (e.g., `https://photos.yourdomain.com`) to `http://localhost:2283`.
3. **Client Setup:**
   * Download the Immich App on iPhone (App Store) or Android (Play Store).
   * Server URL: `https://photos.yourdomain.com`
   * Log in and enable Background Backup.
   * Photos/videos upload automatically from anywhere on cellular data.

### Option B: Tailscale VPN
1. Install Tailscale on the server: `curl -fsSL https://tailscale.com/install.sh | sh && sudo tailscale up`
2. Install Tailscale on your phone and log in to the same account.
3. Connect in Immich using `http://mepitsserver:2283`.

---

## Client Quick Reference Card

| Feature | Access Method |
| :--- | :--- |
| **Physical Chromebook Screen** | Integrated Dashboard with live temperature & 1-click Gallery switcher |
| **Change Wi-Fi Network** | Click top-right notification bar on Chromebook, or open `https://<ip>:9090` |
| **Upload Photos from Laptop** | Open `http://<ip>:2283` in Chrome/Edge -> Drag & drop files |
| **Mobile Phone Photo Backup** | Official Immich App (iOS/Android) with Background Backup enabled |

---

## License
MIT License. Open-source and built using Immich, Ubuntu, and Docker.
