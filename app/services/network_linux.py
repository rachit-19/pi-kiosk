import subprocess
from typing import Optional


# ============================================================
# Utility
# ============================================================

def run(cmd: list) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(result.stderr.strip())

    return result.stdout.strip()


def get_active_connection_by_type(conn_type: str) -> str:
    """
    Returns active connection name for ethernet or wifi
    """
    output = run([
        "nmcli", "-t",
        "-f", "NAME,TYPE,STATE",
        "con", "show", "--active"
    ])

    for line in output.splitlines():
        name, typ, state = line.split(":")
        if typ == conn_type and state == "activated":
            return name

    raise Exception(f"No active {conn_type} connection found")


def get_active_device_by_type(conn_type: str) -> Optional[str]:
    output = run([
        "nmcli", "-t",
        "-f", "DEVICE,TYPE,STATE",
        "dev"
    ])

    for line in output.splitlines():
        device, typ, state = line.split(":")
        if typ == conn_type and state == "connected":
            return device

    return None


# ============================================================
# Ethernet
# ============================================================

def ethernet_dhcp():
    conn = get_active_connection_by_type("ethernet")

    run(["nmcli", "con", "mod", conn,
         "ipv4.method", "auto"])

    run(["nmcli", "con", "up", conn])


def ethernet_static(ip: str, gateway: str, dns: Optional[str] = None):
    conn = get_active_connection_by_type("ethernet")

    run([
        "nmcli", "con", "mod", conn,
        "ipv4.method", "manual",
        "ipv4.addresses", ip,
        "ipv4.gateway", gateway
    ])

    if dns:
        run(["nmcli", "con", "mod", conn,
             "ipv4.dns", dns])

    run(["nmcli", "con", "up", conn])


# ============================================================
# WiFi
# ============================================================

def wifi_connect(ssid: str, password: str):
    run([
        "nmcli", "dev", "wifi", "connect",
        ssid,
        "password", password
    ])


def wifi_dhcp():
    conn = get_active_connection_by_type("wifi")

    run(["nmcli", "con", "mod", conn,
         "ipv4.method", "auto"])

    run(["nmcli", "con", "up", conn])


def wifi_static(ip: str, gateway: str, dns: Optional[str] = None):
    conn = get_active_connection_by_type("wifi")

    run([
        "nmcli", "con", "mod", conn,
        "ipv4.method", "manual",
        "ipv4.addresses", ip,
        "ipv4.gateway", gateway
    ])

    if dns:
        run(["nmcli", "con", "mod", conn,
             "ipv4.dns", dns])

    run(["nmcli", "con", "up", conn])


# ============================================================
# Status
# ============================================================

def get_status():
    output = run([
        "nmcli", "-t",
        "-f", "DEVICE,TYPE,STATE,CONNECTION",
        "dev"
    ])

    for line in output.splitlines():
        device, typ, state, conn = line.split(":")

        if state == "connected":
            ip = run([
                "nmcli", "-g", "IP4.ADDRESS",
                "dev", "show", device
            ])

            return {
                "connected": True,
                "type": typ,
                "device": device,
                "connection": conn,
                "ip": ip
            }

    return {"connected": False}


# ============================================================
# WiFi Scan
# ============================================================

def scan_wifi():
    output = run([
        "nmcli", "-t",
        "-f", "SSID,SIGNAL,SECURITY",
        "dev", "wifi", "list"
    ])

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