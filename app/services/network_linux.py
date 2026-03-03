import subprocess
from typing import Optional

CONNECTION_NAME = "kiosk-eth"


def run(cmd: list) -> str:
    print("RUNNING:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    print("RETURN CODE:", result.returncode)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    if result.returncode != 0:
        raise Exception(result.stderr.strip() or "Command failed")

    return result.stdout.strip()


# ==========================
# DHCP
# ==========================

def ethernet_dhcp():
    run([
        "nmcli", "con", "mod", CONNECTION_NAME,
        "ipv4.method", "auto"
    ])

    run([
        "nmcli", "con", "up", CONNECTION_NAME
    ])


# ==========================
# STATIC
# ==========================

def ethernet_static(ip: str, gateway: str, dns: Optional[str] = None):

    if not ip:
        raise Exception("IP required")

    if "/" not in ip:
        ip = ip + "/24"

    if not gateway:
        raise Exception("Gateway required")

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

    run([
        "nmcli", "con", "up", CONNECTION_NAME
    ])


# ==========================
# STATUS
# ==========================

def get_status():
    output = run([
        "nmcli", "-t",
        "-f", "DEVICE,STATE,CONNECTION",
        "dev", "status"
    ])

    for line in output.splitlines():
        device, state, connection = line.split(":")

        if device == "eth0" and state == "connected":

            ip = run([
                "nmcli", "-g", "IP4.ADDRESS",
                "dev", "show", "eth0"
            ])

            return {
                "connected": True,
                "device": device,
                "connection": connection,
                "ip": ip
            }

    return {"connected": False}