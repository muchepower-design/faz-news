# app/routes/uploads.py
import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from app.auth import admin_required

bp = Blueprint('uploads', __name__)

# ---------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'avif'}
MAX_FILE_SIZE = 10 * 1024 * 1024          # 10 MB
UPLOAD_SUBFOLDER = 'uploads'


def _assets_root():
    """Absolute path to backend/app/assets — where the /assets blueprint serves from."""
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.abspath(os.path.join(here, '..', 'assets'))


def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/image', methods=['POST'])
@jwt_required()
@admin_required
def upload_image():
    if 'file' not in request.files:
        abort(400, 'No file part in the request')

    file = request.files['file']
    if not file or file.filename == '':
        abort(400, 'No file selected')

    if not _allowed_file(file.filename):
        abort(400, f"File type not allowed. Use one of: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    # Size check without loading the whole file twice
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > MAX_FILE_SIZE:
        abort(413, f'File too large. Max {MAX_FILE_SIZE // (1024 * 1024)} MB')

    ext = file.filename.rsplit('.', 1)[1].lower()

    # Optional category groups files into subfolders: hero / partners / governance / pages
    category = secure_filename((request.form.get('category') or 'general').strip().lower()) or 'general'

    # Date-based subfolders keep individual directories small
    now = datetime.utcnow()
    year, month = now.strftime('%Y'), now.strftime('%m')

    abs_dir = os.path.join(_assets_root(), UPLOAD_SUBFOLDER, category, year, month)
    os.makedirs(abs_dir, exist_ok=True)

    # Collision-proof filename
    new_name = f"{uuid.uuid4().hex}.{ext}"
    file.save(os.path.join(abs_dir, new_name))

    # RELATIVE url — frontend resolves it against the API base
    rel_url = f"/assets/{UPLOAD_SUBFOLDER}/{category}/{year}/{month}/{new_name}"
    return jsonify({'url': rel_url, 'filename': new_name, 'size': size}), 201


@bp.route('/image', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_image():
    rel = (request.args.get('path') or '').strip()
    if not rel.startswith(f'/assets/{UPLOAD_SUBFOLDER}/'):
        abort(400, 'Only uploaded files can be deleted')

    abs_path = os.path.abspath(os.path.join(_assets_root(), rel.replace('/assets/', '', 1)))
    root = os.path.abspath(_assets_root())
    if not abs_path.startswith(root):
        abort(400, 'Invalid path')

    if os.path.isfile(abs_path):
        os.remove(abs_path)
    return jsonify({'message': 'Deleted'}), 200