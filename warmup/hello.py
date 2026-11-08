from flask import Flask, jsonify, request

app = Flask(__name__)

ITEMS = {
    1: {"id": 1, "name": "widget", "quantity": 120},
    2: {"id": 2, "name": "gadget", "quantity": 35},
}


@app.get("/")
def index():
    return "Hello from Flask\n"


@app.get("/items")
def list_items():
    # Query string: /items?q=wid
    q = request.args.get("q", "").lower()
    return jsonify([item for item in ITEMS.values() if q in item["name"]])


@app.get("/items/<int:item_id>")
def get_item(item_id):
    # The <int:...> converter means /items/abc never reaches this function.
    item = ITEMS.get(item_id)
    if item is None:
        return jsonify(error=f"item {item_id} not found"), 404
    return item  # A dict return value is serialised to JSON automatically.


@app.post("/items")
def create_item():
    data = request.get_json(silent=True)
    name = data.get("name") if isinstance(data, dict) else None
    if not isinstance(name, str) or not name.strip():
        return {"error": "name is required"}, 400
    new_id = max(ITEMS, default=0) + 1
    item = {"id": new_id, "name": name.strip(), "quantity": int(data.get("quantity", 0))}
    ITEMS[new_id] = item
    return item, 201
