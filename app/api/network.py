from fastapi import APIRouter, HTTPException
from app.services.network_linux import (
    ethernet_dhcp,
    ethernet_static,
    wifi_connect,
    wifi_dhcp,
    wifi_static,
    get_status,
    scan_wifi
)

router = APIRouter(prefix="/api/network", tags=["network"])


# ============================================================
# APPLY NETWORK
# ============================================================

@router.post("/apply")
def apply_network(cfg: dict):
    try:
        network_type = cfg.get("network_type")
        ip_mode = cfg.get("ip_mode")

        if network_type == "ethernet":

            if ip_mode == "dhcp":
                ethernet_dhcp()

            elif ip_mode == "static":
                ethernet_static(
                    cfg.get("pi_ip"),
                    cfg.get("gateway"),
                    cfg.get("dns")
                )

            else:
                raise ValueError("Invalid ip_mode")

        elif network_type == "wifi":

            # Connect first (creates/activates connection)
            wifi_connect(
                cfg.get("wifi_ssid"),
                cfg.get("wifi_password")
            )

            if ip_mode == "dhcp":
                wifi_dhcp()

            elif ip_mode == "static":
                wifi_static(
                    cfg.get("pi_ip"),
                    cfg.get("gateway"),
                    cfg.get("dns")
                )

            else:
                raise ValueError("Invalid ip_mode")

        else:
            raise ValueError("Invalid network_type")

        return {"status": "ok"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# GET CURRENT NETWORK STATUS
# ============================================================

@router.get("/status")
def network_status():
    try:
        return get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# SCAN WIFI NETWORKS
# ============================================================

@router.get("/wifi/scan")
def wifi_scan():
    try:
        return scan_wifi()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# GET CURRENT IP ONLY (lightweight endpoint)
# ============================================================

@router.get("/ip")
def current_ip():
    try:
        status = get_status()
        return {"ip": status.get("ip")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))