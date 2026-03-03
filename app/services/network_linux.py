import subprocess
import threading
import time
from typing import Optional


# ============================================================
# Internal Helpers
# ============================================================

def _run(cmd: list) -> str:
    """
    Execute command and raise proper exception if it fails.
    """
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(result.stderr.strip() or "Command failed")

    return result.stdout.strip()


def _get_ethernet_connection() -> str:
    """
    Auto-detect active ethernet connection name.
    """
    output = _run([
        "nmcli", "-t",
        "-f", "NAME,TYPE",
        "con", "show"
    ])

    for line in output.splitlines():
        name, typ = line.split(":")
        if typ == "ethernet":
            return name

    raise Exception("No ethernet connection found")


def _apply_connection_async(connection: str):
    """
    Bring connection up asynchronously to avoid HTTP drop issues.
    """
    def worker():
        time.sleep(1)
        subprocess.Popen(["nmcli", "con", "up", connection])

    threading.Thread(target=worker, daemon=True).start()


# ============================================================
# Public API
# ============================================================

def ethernet_dhcp():
    """
    Switch ethernet to DHCP.
    """
    connection = _get_ethernet_connection()

    _run([
        "nmcli", "con", "mod", connection,
        "ipv4.method", "auto"
    ])

    _run([
        "nmcli", "con", "mod", connection,
        "ipv4.addresses", "",
        "ipv4.gateway", "",
        "ipv4.dns", ""
    ])

    _apply_connection_async(connection)


def ethernet_static(ip: str, gateway: str, dns: Optional[str] = None):
    """
    Configure ethernet with static IP.
    IP must include CIDR (example: 192.168.1.50/24)
    """

    if not ip or "/" not in ip:
        raise Exception("Invalid IP format. Use CIDR (example: 192.168.1.50/24)")

    if not gateway:
        raise Exception("Gateway required for static configuration")

    connection = _get_ethernet_connection()

    _run([
        "nmcli", "con", "mod", connection,
        "ipv4.method", "manual",
        "ipv4.addresses", ip,
        "ipv4.gateway", gateway
    ])

    if dns:
        _run([
            "nmcli", "con", "mod", connection,
            "ipv4.dns", dns
        ])

    _apply_connection_async(connection)


def get_status():
    """
    Return current ethernet status and IP.
    """
    output = _run([
        "nmcli", "-t",
        "-f", "DEVICE,TYPE,STATE,CONNECTION",
        "dev"
    ])

    for line in output.splitlines():
        device, typ, state, connection = line.split(":")

        if typ == "ethernet" and state == "connected":

            ip = _run([
                "nmcli", "-g", "IP4.ADDRESS",
                "dev", "show", device
            ])

            ip_clean = ip.split("\n")[0] if ip else None

            return {
                "connected": True,
                "device": device,
                "connection": connection,
                "ip": ip_clean
            }

    return {"connected": False}