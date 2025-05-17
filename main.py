# main.py - Stage 1: Backend API Only

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from datetime import datetime

app = FastAPI(
    title="Bertram Labs Coffee Pot API",
    description="API to determine whose turn it is to pay for coffee.",
    version="1.0.0"
)

DATA_FILE = "coffee_pot.json"

# === Models ===

class DrinkerBase(BaseModel):
    name: str
    favorite_drink_cost: float
    favorite_drink_name: str

class DrinkerCreate(DrinkerBase):
    pass

class DrinkerUpdate(BaseModel):
    name: Optional[str] = None
    favorite_drink_cost: Optional[float] = None
    favorite_drink_name: Optional[str] = None

class Drinker(DrinkerBase):
    id: int
    total_paid_into_pot: float
    total_person_drinks_cost: float

    class Config:
        from_attributes = True

class CoffeeRoundResponse(BaseModel):
    message: str
    current_round: dict

# === Helpers ===

def read_data():
    if not os.path.exists(DATA_FILE):
        return {
            "drinkers": [],
            "rounds": []
        }
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def write_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def find_drinker(drinker_id: int):
    data = read_data()
    for d in data["drinkers"]:
        if d["id"] == drinker_id:
            return d
    return None

def find_drinker_name(drinker_name: str):
    data = read_data()
    for d in data["drinkers"]:
        if d["name"] == drinker_name:
            return d
    return None

@app.on_event("startup")
def initialize_data():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "drinkers": [
                {"id": 1, "name": "Bob", "favorite_drink_cost": 4.5, "favorite_drink_name": "Cappuccino", "total_paid_into_pot": 0, "total_person_drinks_cost": 0},
                {"id": 2, "name": "Jeremy", "favorite_drink_cost": 2.5, "favorite_drink_name": "Black Coffee", "total_paid_into_pot": 0, "total_person_drinks_cost": 0},
                {"id": 3, "name": "Jenna", "favorite_drink_cost": 3.75, "favorite_drink_name": "Latte", "total_paid_into_pot": 0, "total_person_drinks_cost": 0},
                {"id": 4, "name": "Jade", "favorite_drink_cost": 3.0, "favorite_drink_name": "Black Cold brew", "total_paid_into_pot": 0, "total_person_drinks_cost": 0},
                {"id": 5, "name": "Kim", "favorite_drink_cost": 4.0, "favorite_drink_name": "Mocha", "total_paid_into_pot": 0, "total_person_drinks_cost": 0},
                {"id": 6, "name": "Colette", "favorite_drink_cost": 3.5, "favorite_drink_name": "Flat White", "total_paid_into_pot": 0, "total_person_drinks_cost": 0},
                {"id": 7, "name": "David", "favorite_drink_cost": 4.25, "favorite_drink_name": "Macchiato", "total_paid_into_pot": 0, "total_person_drinks_cost": 0}
            ],
            "rounds": []
        }
        write_data(default_data)
        print("Initialized default data in coffee_pot.json")

# === Routes ===

@app.get("/drinkers", response_model=List[Drinker])
def get_drinkers():
    data = read_data()
    return data["drinkers"]

@app.get("/drinkers/{drinker_id}", response_model=Drinker)
def get_drinker(drinker_id: int):
    drinker = find_drinker(drinker_id)
    if not drinker:
        raise HTTPException(status_code=404, detail="Drinker not found")
    return drinker

@app.post("/drinkers", response_model=Drinker, status_code=201)
def create_drinker(drinker: DrinkerCreate):
    data = read_data()
    new_id = max((d["id"] for d in data["drinkers"]), default=0) + 1
    new_drinker = {
        "id": new_id,
        "name": drinker.name,
        "favorite_drink_cost": drinker.favorite_drink_cost,
        "favorite_drink_name": drinker.favorite_drink_name,
        "total_paid_into_pot": 0,
        "total_person_drinks_cost": 0
    }
    data["drinkers"].append(new_drinker)
    write_data(data)
    return new_drinker

@app.put("/drinkers/{drinker_id}", response_model=Drinker)
def update_drinker(drinker_id: int, updated_drinker: DrinkerUpdate):
    data = read_data()
    for d in data["drinkers"]:
        if d["id"] == drinker_id:
            if updated_drinker.favorite_drink_cost is not None:
                d["favorite_drink_cost"] = updated_drinker.favorite_drink_cost
            if updated_drinker.favorite_drink_name:
                d["favorite_drink_name"] = updated_drinker.favorite_drink_name
            write_data(data)
            return d
    raise HTTPException(status_code=404, detail="Drinker not found")

@app.delete("/drinkers/{drinker_id}")
def delete_drinker(drinker_id: int):
    data = read_data()
    drinkers = [d for d in data["drinkers"] if d["id"] != drinker_id]
    if len(drinkers) == len(data["drinkers"]):
        raise HTTPException(status_code=404, detail="Drinker not found")
    data["drinkers"] = drinkers
    write_data(data)
    return {"message": "Drinker deleted"}

@app.post("/reset-balances")
def reset_all_balances():
    data = read_data()
    for d in data["drinkers"]:
        d["total_paid_into_pot"] = 0.0
        d["total_person_drinks_cost"] = 0.0
    write_data(data)
    return {"message": "All drinker balances have been reset to 0."}

@app.post("/coffee-rounds", response_model=CoffeeRoundResponse)
def record_coffee_round():
    data = read_data()

    lowest_balance = float('inf')
    selected_payer = None
    for d in data["drinkers"]:
        pot_balance = d["total_paid_into_pot"] - d["total_person_drinks_cost"]
        if pot_balance < lowest_balance:
            lowest_balance = pot_balance
            selected_payer = d

    if not selected_payer:
        raise HTTPException(status_code=500, detail="Could not determine a payer")

    payer_id = selected_payer["id"]
    payer_name = selected_payer["name"]
    total_cost = sum(d["favorite_drink_cost"] for d in data["drinkers"])

    for d in data["drinkers"]:
        if d["id"] == payer_id:
            d["total_paid_into_pot"] += total_cost
        d["total_person_drinks_cost"] += d["favorite_drink_cost"]

    round_entry = {
        "id": len(data["rounds"]) + 1,
        "timestamp": datetime.now().isoformat(),
        "payer_id": payer_id,
        "payer_name": payer_name,
        "total_cost": total_cost
    }
    data["rounds"].append(round_entry)

    next_payer = min(
        data["drinkers"],
        key=lambda d: d["total_paid_into_pot"] - d["total_person_drinks_cost"]
    )

    write_data(data)

    return {
        "message": "Coffee round recorded successfully",
        "current_round": {
            "id": round_entry["id"],
            "timestamp": round_entry["timestamp"],
            "payer_id": payer_id,
            "payer_name": payer_name,
            "total_cost": total_cost,
            "next_payer_id": next_payer["id"],
            "next_payer_name": next_payer["name"],
            "lowest_balance": next_payer["total_paid_into_pot"] - next_payer["total_person_drinks_cost"]
        }
    }

@app.get("/next-payer")
def get_next_payer():
    data = read_data()
    drinkers = data["drinkers"]
    if not drinkers:
        return {}
    next_payer = min(
        drinkers,
        key=lambda d: d["total_paid_into_pot"] - d["total_person_drinks_cost"]
    )
    return {"name": next_payer["name"]}

# === Run the server ===

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)