#!/usr/bin/env python3
import http.server
import socketserver
import json
import psutil
import subprocess
import os
import re

PORT = 8080

def get_tunnel_url():
    try:
        with open('/var/log/mepitscloud-tunnel.log', 'r') as f:
            content = f.read()
            urls = re.findall(r'(https://[a-zA-Z0-9-]+\\.trycloudflare\\.com)', content)
            if urls:
                return urls[-1]
    except:
        pass
    return "https://newcastle-dimension-hart-shots.trycloudflare.com"

HTML_TEMPLATE = \"\"\"<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MepitsCloud | Industrial Server Dashboard</title>
    <style>
        :root {
            --bg-primary: #0a0c10;
            --bg-glass: rgba(18, 22, 28, 0.75);
            --border-glass: rgba(255, 255, 255, 0.08);
            --border-focus: rgba(255, 255, 255, 0.16);
            --text-primary: #ededed;
            --text-secondary: #8b949e;
            --text-muted: #565d68;
            --accent-emerald: #10b981;
            --accent-blue: #3b82f6;
            --accent-orange: #f59e0b;
            --badge-bg: rgba(255, 255, 255, 0.05);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
        body {
            background-color: var(--bg-primary);
            color: var(--text-primary);
            padding: 24px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border-glass);
            margin-bottom: 24px;
        }
        .brand { display: flex; align-items: center; gap: 12px; }
        .logo-box {
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, #1f2937, #111827);
            border: 1px solid var(--border-glass);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 16px;
            color: var(--text-primary);
        }
        .brand-title { font-size: 18px; font-weight: 600; letter-spacing: -0.5px; }
        .brand-subtitle { font-size: 12px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; }
        .live-status { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--text-secondary); }
        .pulse-dot { width: 8px; height: 8px; background: var(--accent-emerald); border-radius: 50%; box-shadow: 0 0 8px var(--accent-emerald); }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 24px; }
        .glass-card {
            background: var(--bg-glass);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--border-glass);
            border-radius: 12px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: border-color 0.2s ease;
        }
        .glass-card:hover { border-color: var(--border-focus); }
        .card-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 12px; }
        .card-title { font-size: 13px; font-weight: 500; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; }
        .card-value { font-size: 28px; font-weight: 700; color: var(--text-primary); letter-spacing: -1px; }
        .card-subtext { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
        .progress-bar-bg { width: 100%; height: 6px; background: rgba(255, 255, 255, 0.05); border-radius: 3px; overflow: hidden; margin-top: 14px; }
        .progress-bar-fill { height: 100%; background: var(--text-primary); border-radius: 3px; transition: width 0.4s ease; }
        .sensor-list { display: flex; flex-direction: column; gap: 8px; margin-top: 8px; }
        .sensor-item { display: flex; justify-content: space-between; align-items: center; font-size: 12px; border-bottom: 1px solid rgba(255,255,255,0.03); padding-bottom: 4px; }
        .sensor-name { color: var(--text-secondary); }
        .sensor-val { font-weight: 600; color: var(--text-primary); font-family: monospace; }
        
        .action-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-top: 8px;
        }
        .action-btn {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border-glass);
            border-radius: 10px;
            padding: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            text-decoration: none;
            color: var(--text-primary);
            transition: all 0.2s ease;
        }
        .action-btn:hover {
            background: rgba(255, 255, 255, 0.08);
            border-color: var(--border-focus);
            transform: translateY(-1px);
        }
        .btn-title { font-size: 14px; font-weight: 600; }
        .btn-sub { font-size: 11px; color: var(--text-secondary); margin-top: 2px; }
        .btn-tag { font-size: 10px; padding: 4px 8px; border-radius: 4px; font-weight: 600; text-transform: uppercase; }
        .tag-local { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
        .tag-remote { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
        .footer { font-size: 11px; color: var(--text-muted); text-align: center; margin-top: 20px; }
    </style>
</head>
<body>
    <div>
        <div class="header">
            <div class="brand">
                <div class="logo-box">M</div>
                <div>
                    <div class="brand-title">MepitsCloud Private Server</div>
                    <div class="brand-subtitle">Intel Celeron C720 · 2TB Expansion Storage</div>
                </div>
            </div>
            <div class="live-status">
                <div class="pulse-dot"></div>
                <span id="uptime-display">System Active</span>
            </div>
        </div>

        <div class="grid">
            <div class="glass-card">
                <div class="card-header">
                    <span class="card-title">Seagate 2TB Storage</span>
                    <span class="card-subtext" id="disk-free">664 GB Free</span>
                </div>
                <div class="card-value" id="disk-percent">65%</div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" id="disk-bar" style="width: 65%;"></div>
                </div>
                <div class="card-subtext" style="margin-top: 10px;">Mounted on /mnt/storage · BigWrites Enabled</div>
            </div>

            <div class="glass-card">
                <div class="card-header">
                    <span class="card-title">CPU Utilization</span>
                    <span class="card-subtext">Intel Celeron</span>
                </div>
                <div class="card-value" id="cpu-percent">12%</div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" id="cpu-bar" style="width: 12%;"></div>
                </div>
                <div class="card-subtext" style="margin-top: 10px;">2 Cores · Minimal OS Profile</div>
            </div>

            <div class="glass-card">
                <div class="card-header">
                    <span class="card-title">System Memory</span>
                    <span class="card-subtext" id="ram-used">1.2 / 3.2 GB</span>
                </div>
                <div class="card-value" id="ram-percent">38%</div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" id="ram-bar" style="width: 38%;"></div>
                </div>
                <div class="card-subtext" style="margin-top: 10px;">Low-RAM PostgreSQL Tuned</div>
            </div>

            <div class="glass-card">
                <div class="card-header">
                    <span class="card-title">Hardware Telemetry</span>
                    <span class="card-subtext">Sensors</span>
                </div>
                <div class="sensor-list">
                    <div class="sensor-item">
                        <span class="sensor-name">CPU Core</span>
                        <span class="sensor-val" id="cpu-temp">48.0 °C</span>
                    </div>
                    <div class="sensor-item">
                        <span class="sensor-name">Seagate 2TB HDD</span>
                        <span class="sensor-val" id="hdd-temp">34.0 °C</span>
                    </div>
                    <div class="sensor-item">
                        <span class="sensor-name">Cooling Fan</span>
                        <span class="sensor-val">3,700 RPM</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="action-container">
            <a href="http://mepitscloud.local:2283" class="action-btn" target="_blank">
                <div>
                    <div class="btn-title">Local Gallery Access</div>
                    <div class="btn-sub">http://mepitscloud.local:2283</div>
                </div>
                <span class="btn-tag tag-local">Local LAN</span>
            </a>

            <a id="remote-tunnel-btn" href="{TUNNEL_URL}" class="action-btn" target="_blank">
                <div>
                    <div class="btn-title">Remote 5G Access Tunnel</div>
                    <div class="btn-sub" id="tunnel-subtext">{TUNNEL_URL}</div>
                </div>
                <span class="btn-tag tag-remote">Global 5G</span>
            </a>
        </div>
    </div>

    <div class="footer">
        MepitsCloud OS · Continuous System Health & Automated Backup
    </div>

    <script>
        async function fetchStats() {
            try {
                const res = await fetch('/api/stats');
                const data = await res.json();
                
                document.getElementById('cpu-percent').innerText = data.cpu_percent + '%';
                document.getElementById('cpu-bar').style.width = data.cpu_percent + '%';
                
                document.getElementById('ram-percent').innerText = data.ram_percent + '%';
                document.getElementById('ram-bar').style.width = data.ram_percent + '%';
                document.getElementById('ram-used').innerText = data.ram_used + ' / ' + data.ram_total + ' GB';
                
                document.getElementById('disk-percent').innerText = data.disk_percent + '%';
                document.getElementById('disk-bar').style.width = data.disk_percent + '%';
                document.getElementById('disk-free').innerText = data.disk_free + ' GB Free';
                
                if (data.cpu_temp) document.getElementById('cpu-temp').innerText = data.cpu_temp + ' °C';
                if (data.hdd_temp) document.getElementById('hdd-temp').innerText = data.hdd_temp + ' °C';
                if (data.tunnel_url) {
                    document.getElementById('remote-tunnel-btn').href = data.tunnel_url;
                    document.getElementById('tunnel-subtext').innerText = data.tunnel_url;
                }
            } catch (e) {
                console.error("Stats poll error:", e);
            }
        }
        setInterval(fetchStats, 2500);
        fetchStats();
    </script>
</body>
</html>
\"\"\"

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            cpu_pct = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/mnt/storage') if os.path.exists('/mnt/storage') else psutil.disk_usage('/')
            
            stats = {
                "cpu_percent": round(cpu_pct, 1),
                "ram_percent": round(mem.percent, 1),
                "ram_used": round(mem.used / (1024**3), 2),
                "ram_total": round(mem.total / (1024**3), 2),
                "disk_percent": round(disk.percent, 1),
                "disk_free": round(disk.free / (1024**3), 1),
                "cpu_temp": 48.0,
                "hdd_temp": 34.0,
                "tunnel_url": get_tunnel_url()
            }
            self.wfile.write(json.dumps(stats).encode())
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            rendered = HTML_TEMPLATE.replace("{TUNNEL_URL}", get_tunnel_url())
            self.wfile.write(rendered.encode())

if __name__ == '__main__':
    with socketserver.TCPServer(("0.0.0.0", PORT), DashboardHandler) as httpd:
        print(f"Serving MepitsCloud Dashboard on port {PORT}")
        httpd.serve_forever()
