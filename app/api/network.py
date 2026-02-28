import subprocess

from pydantic import BaseModel, Field
from typing import Optional


class NetworkConfig(BaseModel):
    network_type: str = Field(..., pattern="^(ethernet|wifi)$")
    ip_mode: str = Field(..., pattern="^(dhcp|static)$")

    pi_ip: Optional[str] = None
    gateway: Optional[str] = None
    dns: Optional[str] = None

    wifi_ssid: Optional[str] = None
    wifi_password: Optional[str] = None

def run(cmd: list):
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(result.stderr.strip())

    return result.stdout.strip()


# ===============================
# Ethernet
# ===============================

def ethernet_dhcp():
    run(["nmcli", "con", "mod", "Wired connection 1",
         "ipv4.method", "auto"])
    run(["nmcli", "con", "up", "Wired connection 1"])


def ethernet_static(ip, gateway, dns=None):
    run(["nmcli", "con", "mod", "Wired connection 1",
         "ipv4.method", "manual",
         "ipv4.addresses", ip,
         "ipv4.gateway", gateway])

    if dns:
        run(["nmcli", "con", "mod", "Wired connection 1",
             "ipv4.dns", dns])

    run(["nmcli", "con", "up", "Wired connection 1"])


# ===============================
# WiFi
# ===============================

def wifi_connect(ssid, password):
    # Try connect (will auto create connection)
    run([
        "nmcli", "dev", "wifi", "connect",
        ssid,
        "password", password
    ])


def wifi_dhcp():
    run(["nmcli", "con", "mod",
         get_active_wifi_connection(),
         "ipv4.method", "auto"])
    run(["nmcli", "con", "up",
         get_active_wifi_connection()])


def wifi_static(ip, gateway, dns=None):
    con = get_active_wifi_connection()

    run(["nmcli", "con", "mod", con,
         "ipv4.method", "manual",
         "ipv4.addresses", ip,
         "ipv4.gateway", gateway])

    if dns:
        run(["nmcli", "con", "mod", con,
             "ipv4.dns", dns])

    run(["nmcli", "con", "up", con])


def get_active_wifi_connection():
    output = run(["nmcli", "-t", "-f", "NAME,DEVICE",
                  "con", "show", "--active"])

    for line in output.splitlines():
        name, device = line.split(":")
        if device == "wlan0":
            return name

    raise Exception("No active WiFi connection found")


# ===============================
# Status
# ===============================

def get_status():
    wifi = run(["nmcli", "-t", "-f",
                "ACTIVE,SSID,DEVICE",
                "dev", "wifi"])

    for line in wifi.splitlines():
        parts = line.split(":")
        if parts[0] == "yes":
            return {
                "connected": True,
                "interface": "wifi",
                "ssid": parts[1]
            }

    eth = run(["nmcli", "-t", "-f",
               "DEVICE,STATE", "device"])

    if "eth0:connected" in eth:
        return {
            "connected": True,
            "interface": "ethernet"
        }

    return {"connected": False}


# ===============================
# Scan WiFi
# ===============================

def scan_wifi():
    output = run(["nmcli", "-t", "-f",
                  "SSID,SIGNAL,SECURITY",
                  "dev", "wifi", "list"])

    networks = []

    for line in output.splitlines():
        parts = line.split(":")
        if parts[0]:
            networks.append({
                "ssid": parts[0],
                "signal": parts[1],
                "security": parts[2]
            })

    return networks