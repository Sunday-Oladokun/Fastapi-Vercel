# Import necessary modules from FastAPI and standard libraries
from fastapi import FastAPI, HTTPException  # FastAPI core and HTTP error handling
from pydantic import BaseModel              # For data validation and serialization
from fastapi.responses import FileResponse  # To serve files (used for favicon)
from fastapi.staticfiles import StaticFiles  # To serve static files like favicon
import os  # Standard library for file path operations

# Create an instance of the FastAPI app
app = FastAPI()

# Define a Pydantic model for an item
class Item(BaseModel):
    name: str
    description: str | None = None  # Optional field
    price: float

# In-memory storage for items (acts like a temporary database)
items = []

# Root endpoint: returns a simple welcome message
@app.get("/")
def root():
    return {"Hello": "World"}

# Endpoint to create a new item and add it to the list
@app.post("/items")
def create_item(item: Item):
    items.append(item)
    return items

# Endpoint to list items with an optional limit (default is 10)
@app.get("/items", response_model=list[Item])
def list_items(limit: int = 10):
    return items[0:limit]

# Endpoint to retrieve a specific item by ID
@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    if item_id < len(items):
        return items[item_id]
    # Raise a 404 error if the item ID is out of range
    raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

# Endpoint to delete a specific item by ID
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id < len(items):
        removed_item = items.pop(item_id)
        return {"message": f"Item {item_id} deleted", "item": removed_item}
    # Raise a 404 error if the item ID is invalid
    raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

# Endpoint to update an existing item by ID
@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: Item):
    if item_id < len(items):
        items[item_id] = item
        return items[item_id]
    # Raise a 404 error if the item ID is invalid
    raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

# ---- Vercel-specific configuration for serving static files and favicon ----

# Construct the file path for the favicon
favicon_path = os.path.join(os.path.dirname(__file__), "..", "static", "favicon.ico")

# Mount the static directory so static files (e.g. images, favicon) can be served
app.mount("/static", StaticFiles(directory="../static"), name="static")

# Endpoint to serve the favicon.ico file (excluded from automatic docs)
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)