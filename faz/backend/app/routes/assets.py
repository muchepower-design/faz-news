# app/routes/assets.py
import os
from flask import Blueprint, send_from_directory, abort, jsonify

bp = Blueprint('assets', __name__)

# __file__ is  backend/app/routes/assets.py
#   dirname  → backend/app/routes
#   ..       → backend/app
#   +assets  → backend/app/assets   ✅
_ASSETS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'assets')
)

print("=" * 70)
print(f"[assets] __file__     = {__file__}")
print(f"[assets] _ASSETS_DIR  = {_ASSETS_DIR}")
print(f"[assets] exists?      = {os.path.isdir(_ASSETS_DIR)}")
if os.path.isdir(_ASSETS_DIR):
    print(f"[assets] top-level    = {os.listdir(_ASSETS_DIR)}")
print("=" * 70)


@bp.route('/debug', methods=['GET'])
def debug():
    exists = os.path.isdir(_ASSETS_DIR)
    tree = {}
    if exists:
        for root, _dirs, files in os.walk(_ASSETS_DIR):
            rel = os.path.relpath(root, _ASSETS_DIR)
            tree[rel] = files
    return jsonify({
        "assets_dir": _ASSETS_DIR,
        "exists": exists,
        "tree": tree,
    })


@bp.route('/<path:filename>', methods=['GET'])
def serve_asset(filename):
    requested = os.path.abspath(os.path.join(_ASSETS_DIR, filename))
    print(f"[assets] GET {filename} -> {requested}  isfile? {os.path.isfile(requested)}")

    if not requested.startswith(_ASSETS_DIR):
        abort(404)
    if not os.path.isfile(requested):
        abort(404)

    return send_from_directory(_ASSETS_DIR, filename)