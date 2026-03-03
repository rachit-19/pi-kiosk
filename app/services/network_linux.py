import subprocess
from typing import Optional


CONNECTION_NAME = "kiosk-eth"  # Change if needed


# ============================================================
# Utility
# ============================================================

def run(cmd: list) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(result.stderr.strip())

    return result.stdout.strip()


# ============================================================
# Ethernet DHCP
# ============================================================

def ethernet_dhcp():
    run([
        "nmcli", "con", "mod", CONNECTION_NAME,
        "ipv4.method", "auto"
    ])

    run(["nmcli", "con", "up", CONNECTION_NAME])


# ============================================================
# Ethernet Static
# ============================================================

def ethernet_static(ip: str, gateway: str, dns: Optional[str] = None):

    if not ip or not gateway:
        raise Exception("IP and Gateway required for static mode")

    run([
        "nmcli", "con", "mod", CONNECTION_NAME,
        "ipv4.method", "manual",
        "ipv4.addresses", ip,
        "ipv4.gateway", gateway
    ])

    if dns:
        run([
            "nmcli", "con", "mod", CONNECTION_NAME,
            "ipv4.dns", dns
        ])

    run(["nmcli", "con", "up", CONNECTION_NAME])


# ============================================================
# Status
# ============================================================

def get_status():

    output = run([
        "nmcli", "-t",
        "-f", "DEVICE,STATE,CONNECTION",
        "dev"
    ])

    for line in output.splitlines():
        device, state, connection = line.split(":")

        if state == "connected" and connection == CONNECTION_NAME:

            ip = run([
                "nmcli", "-g", "IP4.ADDRESS",
                "dev", "show", device
            ])

            return {
                "connected": True,
                "device": device,
                "ip": ip
            }

    return {"connected": False}