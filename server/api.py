from fastapi import FastAPI, HTTPException, Body
from typing import Dict, Any
from server.models import SaveStateV2, PurchaseRecord
from server.storage import GameDatabase
from server.sync_engine import AuthoritativeSyncEngine
from server.currency_engine import CurrencySplitEngine
from server.store_engine import GemStoreEngine
from server.legacy_adapter import LegacyClientAdapter

app = FastAPI(title="Merge Kingdom Live-Ops Sync & Economy Backend", version="2.5.0")

# Initialize singleton services
db = GameDatabase()
sync_engine = AuthoritativeSyncEngine(db)
currency_engine = CurrencySplitEngine(db)
store_engine = GemStoreEngine(db)
legacy_adapter = LegacyClientAdapter(db, sync_engine)

@app.get("/health")
def health():
    return {"status": "HEALTHY", "version": "2.5.0", "game": "Merge Kingdom"}

@app.post("/api/v1/sync")
def sync_v1_legacy(payload: Dict[str, Any] = Body(...)):
    """
    Legacy sync endpoint for app versions 2.0 through 2.4 and non-updatable Android 7 devices.
    Accepts v1 JSON and returns pure v1 JSON without crashing legacy JsonUtility.
    """
    if "player_id" not in payload:
        raise HTTPException(status_code=400, detail="Missing player_id in legacy payload")
    
    response_json = legacy_adapter.handle_legacy_upload(payload)
    return response_json

@app.post("/api/v2/sync")
def sync_v2_modern(save_dict: Dict[str, Any] = Body(...)):
    """
    Authoritative Version 2.5 sync endpoint.
    Enforces monotonic levels, sticky entitlements, and revision sequence management.
    """
    if "player_id" not in save_dict:
        raise HTTPException(status_code=400, detail="Missing player_id")
    
    client_save = SaveStateV2.from_dict(save_dict)
    merged_save, meta = sync_engine.sync(client_save)
    return {
        "status": "SUCCESS",
        "save": merged_save.to_dict(),
        "meta": meta
    }

@app.post("/api/v2/migrate")
def migrate_currency(payload: Dict[str, Any] = Body(...)):
    """
    Executes the Task 4 FIFO Payer-Protection Ledger Split for a player.
    """
    player_id = payload.get("player_id")
    if not player_id:
        raise HTTPException(status_code=400, detail="Missing player_id")

    save = db.get_save(player_id)
    if not save:
        raise HTTPException(status_code=404, detail="Player save not found")

    updated_save, split_summary = currency_engine.execute_migration(save)
    return {
        "status": "SUCCESS",
        "split_summary": split_summary,
        "save": updated_save.to_dict()
    }

@app.post("/api/v2/store/buy")
def buy_item(payload: Dict[str, Any] = Body(...)):
    """
    Authoritative store purchase for gems.
    """
    player_id = payload.get("player_id")
    item = payload.get("item")
    if not player_id or not item:
        raise HTTPException(status_code=400, detail="Missing player_id or item")

    success, msg, data = store_engine.purchase_store_item(player_id, item)
    if not success:
        raise HTTPException(status_code=400, detail={"reason": msg, "data": data})

    return {"status": "SUCCESS", "message": msg, "data": data}

@app.post("/api/v2/iap/verify")
def verify_iap(payload: Dict[str, Any] = Body(...)):
    """
    Verifies receipt and credits hard currency gems.
    """
    player_id = payload.get("player_id")
    pack_id = payload.get("pack_id")
    gems = payload.get("gems", 0)
    receipt_id = payload.get("receipt_id", "sim_receipt")

    if not player_id or not pack_id or gems <= 0:
        raise HTTPException(status_code=400, detail="Invalid IAP parameters")

    success, result = store_engine.fulfill_gem_iap(player_id, pack_id, gems, receipt_id)
    return {"status": "SUCCESS", "result": result}

@app.get("/api/v2/debug/player/{player_id}")
def debug_player(player_id: str):
    save = db.get_save(player_id)
    purchases = db.get_purchases(player_id)
    gem_logs = db.get_gem_ledger(player_id)
    return {
        "save": save.to_dict() if save else None,
        "purchases": [p.__dict__ for p in purchases],
        "gem_ledger": gem_logs
    }

