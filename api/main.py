# Import necessary modules from FastAPI and standard libraries
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Create an instance of the FastAPI app
app = FastAPI(title="Item API", 
             description="A simple CRUD API for items",
             version="1.0.0")

# Define a Pydantic model for an item
class Item(BaseModel):
    name: str
    description: str | None = None  # Optional field
    price: float

# In-memory storage for items (acts like a temporary database)
items = []

# ---- API Endpoints ----

# Root endpoint: returns a simple welcome message
@app.get("/", tags=["Root"])
def root():
    return {"Hello": "World", "docs": "/docs"}

# Endpoint to create a new item and add it to the list
@app.post("/items", tags=["Items"], response_model=list[Item])
def create_item(item: Item):
    items.append(item)
    return items

# Endpoint to list items with an optional limit (default is 10)
@app.get("/items", tags=["Items"], response_model=list[Item])
def list_items(limit: int = 10):
    return items[0:limit]

# Endpoint to retrieve a specific item by ID
@app.get("/items/{item_id}", tags=["Items"], response_model=Item)
def get_item(item_id: int):
    if item_id < len(items):
        return items[item_id]
    raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

# Endpoint to delete a specific item by ID
@app.delete("/items/{item_id}", tags=["Items"])
def delete_item(item_id: int):
    if item_id < len(items):
        removed_item = items.pop(item_id)
        return {"message": f"Item {item_id} deleted", "item": removed_item}
    raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

# Endpoint to update an existing item by ID
@app.put("/items/{item_id}", tags=["Items"], response_model=Item)
def update_item(item_id: int, item: Item):
    if item_id < len(items):
        items[item_id] = item
        return items[item_id]
    raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

# ---- Vercel-specific configuration ----

# More reliable path handling for favicon
favicon_path = Path(__file__).parent.parent / "static" / "favicon.ico"

# Mount static directory with error handling
try:
    app.mount("/static", StaticFiles(directory="../static"), name="static")
except:
    # Create static directory if it doesn't exist
    os.makedirs("../static", exist_ok=True)
    app.mount("/static", StaticFiles(directory="../static"), name="static")

# Favicon endpoint with existence check
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    if not favicon_path.exists():
        # Create empty favicon if missing
        with open(favicon_path, "wb") as f:
            f.write(b"")
    return FileResponse(favicon_path)