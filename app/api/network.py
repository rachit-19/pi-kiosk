from fastapi import APIRouter, HTTPException
from app.services.network_linux import *

router = APIRouter(prefix="/api/network", tags=["network"])


@router.post("/apply")
def apply_network(cfg: dict):
    try:
        if cfg["network_type"] == "ethernet":
            if cfg["ip_mode"] == "dhcp":
                ethernet_dhcp()
            else:
                ethernet_static(
                    cfg["static_ip"],
                    cfg["gateway"],
                    cfg.get("dns")
                )

        elif cfg["network_type"] == "wifi":
            wifi_connect(cfg["wifi_ssid"], cfg["wifi_password"])

            if cfg["ip_mode"] == "dhcp":
                wifi_dhcp()
            else:
                wifi_static(
                    cfg["static_ip"],
                    cfg["gateway"],
                    cfg.get("dns")
                )

        else:
            raise ValueError("Invalid network type")

        return {"status": "ok"}

    except Exception as e:
        raise HTTPException(500, str(e))