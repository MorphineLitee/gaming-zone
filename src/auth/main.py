from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

app = FastAPI(title="Simple FastAPI App", version="1.0.0")

# ---- Models ----
class ItemIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    price: float = Field(..., ge=0)
    tags: List[str] = []

class Item(ItemIn):
    id: UUID

# ---- In-memory "DB" ----
DB: dict[UUID, Item] = {}

# ---- Health / root ----
@app.get("/", tags=["system"])
async def root():
    return {"message": "FastAPI is up ✅"}

@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok"}

# ---- CRUD: Items ----
@app.post("/items", response_model=Item, status_code=201, tags=["items"])
async def create_item(payload: ItemIn):
    new_item = Item(id=uuid4(), **payload.model_dump())
    DB[new_item.id] = new_item
    return new_item

@app.get("/items", response_model=List[Item], tags=["items"])
async def list_items(tag: Optional[str] = Query(None, description="Filter by tag")):
    items = list(DB.values())
    if tag:
        items = [i for i in items if tag in i.tags]
    return items

@app.get("/items/{item_id}", response_model=Item, tags=["items"])
async def get_item(item_id: UUID):
    item = DB.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.put("/items/{item_id}", response_model=Item, tags=["items"])
async def update_item(item_id: UUID, payload: ItemIn):
    if item_id not in DB:
        raise HTTPException(status_code=404, detail="Item not found")
    updated = Item(id=item_id, **payload.model_dump())
    DB[item_id] = updated
    return updated

@app.delete("/items/{item_id}", status_code=204, tags=["items"])
async def delete_item(item_id: UUID):
    if item_id not in DB:
        raise HTTPException(status_code=404, detail="Item not found")
    del DB[item_id]
    return
