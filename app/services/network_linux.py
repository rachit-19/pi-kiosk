import subprocess


def run(cmd):
    subprocess.run(cmd, check=True)


def get_active_connection(conn_type: str) -> str:
    out = subprocess.check_output(
        ["nmcli", "-t", "-f", "NAME,TYPE,STATE", "con", "show", "--active"]
    ).decode()

    for line in out.splitlines():
        name, ctype, state = line.split(":")
        if ctype == conn_type and state == "activated":
            return name

    raise RuntimeError(f"No active {conn_type} connection")


# ---------- ETHERNET ----------

def ethernet_dhcp():
    conn = get_active_connection("ethernet")
    run(["sudo", "nmcli", "con", "mod", conn, "ipv4.method", "auto"])
    run(["sudo", "nmcli", "con", "up", conn])


def ethernet_static(ip, gw, dns):
    conn = get_active_connection("ethernet")

    cmd = [
        "sudo", "nmcli", "con", "mod", conn,
        "ipv4.method", "manual",
        "ipv4.addresses", ip,
        "ipv4.gateway", gw
    ]

    if dns:
        cmd += ["ipv4.dns", dns]

    run(cmd)
    run(["sudo", "nmcli", "con", "up", conn])


# ---------- WIFI ----------

def wifi_connect(ssid, password):
    run([
        "sudo", "nmcli", "dev", "wifi",
        "connect", ssid,
        "password", password
    ])


def wifi_dhcp():
    conn = get_active_connection("wifi")
    run(["sudo", "nmcli", "con", "mod", conn, "ipv4.method", "auto"])
    run(["sudo", "nmcli", "con", "up", conn])


def wifi_static(ip, gw, dns):
    conn = get_active_connection("wifi")

    cmd = [
        "sudo", "nmcli", "con", "mod", conn,
        "ipv4.method", "manual",
        "ipv4.addresses", ip,
        "ipv4.gateway", gw
    ]

    if dns:
        cmd += ["ipv4.dns", dns]

    run(cmd)
    run(["sudo", "nmcli", "con", "up", conn])