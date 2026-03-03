from fastapi import APIRouter, HTTPException
from app.services.network_linux import (
    ethernet_dhcp,
    ethernet_static,
    get_status
)

router = APIRouter(prefix="/api/network", tags=["network"])


# ============================================================
# APPLY NETWORK
# ============================================================

@router.post("/apply")
def apply_network(cfg: dict):
    try:
        ip_mode = cfg.get("ip_mode")

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

        return {"status": "ok"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# STATUS
# ============================================================

@router.get("/status")
def network_status():
    try:
        return get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# IP ONLY
# ============================================================

@router.get("/ip")
def current_ip():
    try:
        status = get_status()
        return {"ip": status.get("ip")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))