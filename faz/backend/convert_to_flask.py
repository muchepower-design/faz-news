#!/usr/bin/env python3
"""
Enhanced FastAPI → Flask Converter with Model/Schema Splitting
--------------------------------------------------------------
This script:
- Converts FastAPI project (app/) to Flask (flask_backend/)
- Splits models.py into individual files under app/models/
- Splits schemas.py into individual files under app/schemas/
- Transforms all routes, removes async, adapts dependencies, etc.

Run it from the project root (where the 'app' folder is).
"""

import os
import re
import shutil
import ast
import inspect
from pathlib import Path
from typing import Dict, List, Set

# =============================================================================
# CONFIGURATION
# =============================================================================
SOURCE_DIR = Path("app")
OUTPUT_DIR = Path("flask_backend")
PYTHON_EXT = ".py"
EXCLUDED_DIRS = {"__pycache__", ".git"}

# =============================================================================
# UTILITY FUNCTIONS FOR SPLITTING MODELS AND SCHEMAS
# =============================================================================

def parse_classes_from_file(filepath: Path, class_type: str = "model") -> Dict[str, str]:
    """
    Extract class definitions from a Python file.
    class_type: 'model' or 'schema'
    Returns dict {class_name: class_source_code}
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse the file into an AST
    tree = ast.parse(content)

    classes = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Get the source code of the class
            # We need to locate the class block in the original text
            # Use ast.get_source_segment (Python 3.8+)
            try:
                source = ast.get_source_segment(content, node)
                if source:
                    classes[node.name] = source
            except Exception:
                # fallback: manually get lines
                lines = content.splitlines()
                start_line = node.lineno - 1
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else len(lines)
                class_source = "\n".join(lines[start_line:end_line])
                classes[node.name] = class_source
    return classes


def split_models(input_file: Path, output_dir: Path) -> List[str]:
    """
    Split models.py into separate files per model class.
    Also extract enums and base classes (Base, etc.) into a shared file.
    Returns list of created model names.
    """
    models_dir = output_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    # First, read the whole models.py content to capture imports and other top-level stuff
    with open(input_file, 'r', encoding='utf-8') as f:
        full_content = f.read()

    # Extract imports and other top-level lines (before first class)
    # We'll split at first class definition
    lines = full_content.splitlines()
    top_lines = []
    class_start_index = 0
    for i, line in enumerate(lines):
        if re.match(r'^class\s+', line):
            class_start_index = i
            break
        top_lines.append(line)
    # Also include lines after class definitions? Usually not needed.
    top_code = "\n".join(top_lines)

    # Parse classes
    classes = parse_classes_from_file(input_file, "model")

    # Also find association tables (e.g., news_tags = Table(...))
    # We'll extract them and put in a separate file "associations.py"
    association_table_pattern = re.compile(r'^\s*(\w+)\s*=\s*Table\s*\(', re.MULTILINE)
    associations = {}
    for match in association_table_pattern.finditer(full_content):
        table_name = match.group(1)
        # Get the whole assignment statement until the next line that is not part of it
        start = match.start()
        # Find the end of the Table(...) by counting parentheses
        paren_count = 0
        end = start
        for i in range(start, len(full_content)):
            if full_content[i] == '(':
                paren_count += 1
            elif full_content[i] == ')':
                paren_count -= 1
                if paren_count == 0:
                    end = i + 1
                    break
        assignment = full_content[start:end]
        associations[table_name] = assignment

    # Write top_code to a base file (imports, enums, Base)
    base_file = models_dir / "_base.py"
    with open(base_file, 'w', encoding='utf-8') as f:
        # Write imports, enums, Base, and any top-level definitions
        # We also need to add all imports needed for models
        f.write(top_code)
        # Add any missing imports? We'll assume they are already there.
        # Also ensure we have from . import relationship etc.

    # Write associations.py
    if associations:
        assoc_file = models_dir / "associations.py"
        with open(assoc_file, 'w', encoding='utf-8') as f:
            f.write("# Association tables\n")
            for name, code in associations.items():
                f.write(code + "\n\n")

    # Write each model class to its own file
    model_names = []
    for class_name, class_code in classes.items():
        # Skip if it's a base class or enum? We'll filter.
        if class_name in ("Base", "UserRole", "MatchEventType", "Gender", "LeagueLevel", "MatchType", "TournamentCategory"):
            # These are likely defined in top_code, so we skip
            continue
        # Also skip if it's an association table class (if any) – we already extracted
        # For models, we want all SQLAlchemy model classes
        filename = f"{class_name.lower()}.py"
        filepath = models_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            # Write the class code
            f.write(class_code)
        model_names.append(class_name)

    # Now we need to fix imports in each model file: they should import Base from ._base, and other models as needed.
    # We'll add a fix later, but we can generate a __init__.py that imports all models.
    init_content = "# Auto-generated __init__.py\n"
    for name in model_names:
        init_content += f"from .{name.lower()} import {name}\n"
    # Also import Base, enums, associations
    init_content += "from ._base import *\n"
    if associations:
        init_content += "from .associations import *\n"

    with open(models_dir / "__init__.py", 'w', encoding='utf-8') as f:
        f.write(init_content)

    # Also generate a __all__ list for convenience
    all_models = model_names + ["Base"] + list(associations.keys())
    all_list = f"__all__ = {all_models}"
    with open(models_dir / "__init__.py", 'a', encoding='utf-8') as f:
        f.write("\n" + all_list)

    return model_names


def split_schemas(input_file: Path, output_dir: Path) -> List[str]:
    """
    Split schemas.py into separate files per schema class.
    """
    schemas_dir = output_dir / "schemas"
    schemas_dir.mkdir(parents=True, exist_ok=True)

    with open(input_file, 'r', encoding='utf-8') as f:
        full_content = f.read()

    # Extract top-level imports and enums
    lines = full_content.splitlines()
    top_lines = []
    class_start_index = 0
    for i, line in enumerate(lines):
        if re.match(r'^class\s+', line):
            class_start_index = i
            break
        top_lines.append(line)
    top_code = "\n".join(top_lines)

    # Parse classes
    classes = parse_classes_from_file(input_file, "schema")

    # Write top_code to _base.py in schemas
    base_file = schemas_dir / "_base.py"
    with open(base_file, 'w', encoding='utf-8') as f:
        f.write(top_code)

    # Write each schema class
    schema_names = []
    for class_name, class_code in classes.items():
        # Skip enums (they are in top_code)
        if class_name in ("UserRoleEnum", "MatchEventType", "Gender", "LeagueLevel", "MatchType", "TournamentCategory"):
            continue
        filename = f"{class_name.lower()}.py"
        filepath = schemas_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(class_code)
        schema_names.append(class_name)

    # __init__.py
    init_content = "# Auto-generated __init__.py\n"
    for name in schema_names:
        init_content += f"from .{name.lower()} import {name}\n"
    init_content += "from ._base import *\n"
    with open(schemas_dir / "__init__.py", 'w', encoding='utf-8') as f:
        f.write(init_content)

    all_schemas = schema_names + ["UserRoleEnum", "MatchEventType", "Gender", "LeagueLevel", "MatchType", "TournamentCategory"]
    all_list = f"__all__ = {all_schemas}"
    with open(schemas_dir / "__init__.py", 'a', encoding='utf-8') as f:
        f.write("\n" + all_list)

    return schema_names


# =============================================================================
# FILE TRANSFORMATION FUNCTIONS (same as before, with adjustments for imports)
# =============================================================================

def transform_imports(content: str) -> str:
    """Replace FastAPI imports with Flask equivalents and update model/schema imports."""
    # General FastAPI -> Flask
    replacements = [
        (r"from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Query, Body, Path, Header",
         "from flask import Flask, Blueprint, request, jsonify, abort, make_response"),
        (r"from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm",
         "from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required, verify_jwt_in_request"),
        (r"from fastapi.middleware.cors import CORSMiddleware",
         "from flask_cors import CORS"),
        (r"from fastapi.staticfiles import StaticFiles",
         ""),
        (r"from fastapi.responses import Response",
         "from flask import Response"),
        (r"from pydantic import BaseModel",
         "from pydantic import BaseModel"),
    ]
    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    # Update model imports: from .. import models -> from ..models import (class)
    # We'll leave as is; the __init__.py will allow importing.
    return content


def transform_decorators(content: str) -> str:
    """Convert route decorators."""
    methods_map = {
        "get": "GET",
        "post": "POST",
        "put": "PUT",
        "delete": "DELETE",
        "patch": "PATCH",
        "options": "OPTIONS",
        "head": "HEAD",
    }
    for fastapi_method, http_method in methods_map.items():
        pattern = rf'@(\w+)\.{fastapi_method}\(([^)]*)\)'
        repl = rf'@\1.route(\2, methods=["{http_method}"])'
        content = re.sub(pattern, repl, content)
    return content


def transform_path_params(content: str) -> str:
    """Replace {param} with <param> in route strings."""
    def replace_in_route_line(match):
        line = match.group(0)
        line = re.sub(r'\{([^}]+)\}', r'<\1>', line)
        return line
    content = re.sub(r'^.*@\w+\.route\(.*$', replace_in_route_line, content, flags=re.MULTILINE)
    return content


def transform_dependencies(content: str) -> str:
    """Remove Depends, keep parameters."""
    content = re.sub(r',?\s*\bDepends\([^)]*\)', '', content)
    content = re.sub(r'\s*=\s*Depends\([^)]*\)', '', content)
    return content


def transform_async(content: str) -> str:
    """Remove async/await."""
    content = re.sub(r'^(\s*)async\s+def\s+', r'\1def ', content, flags=re.MULTILINE)
    content = re.sub(r'\bawait\s+', '', content)
    return content


def transform_exceptions(content: str) -> str:
    """Convert HTTPException to abort."""
    content = re.sub(r'raise HTTPException\(status_code=(\d+),\s*detail=([^)]*)\)', r'abort(\1, \2)', content)
    return content


def transform_response_model(content: str) -> str:
    """Remove response_model from decorators."""
    content = re.sub(r',?\s*response_model\s*=\s*[^,)]+', '', content)
    return content


def transform_router_to_blueprint(content: str, filename: Path) -> str:
    """Convert APIRouter to Blueprint."""
    if re.search(r'router\s*=\s*APIRouter\(', content):
        bp_name = filename.stem
        content = re.sub(
            r'router\s*=\s*APIRouter\([^)]*\)',
            f"bp = Blueprint('{bp_name}', __name__)",
            content
        )
        content = re.sub(r'@router\.', '@bp.', content)
    content = re.sub(r'from fastapi import.*APIRouter', 'from flask import Blueprint', content)
    return content


def transform_main_py(content: str) -> str:
    """Special handling for main.py."""
    content = re.sub(r'app\s*=\s*FastAPI\([^)]*\)', "app = Flask(__name__)", content)

    # Add CORS and JWT setup after app creation
    cors_setup = """
# CORS
CORS(app)

# JWT
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
jwt = JWTManager(app)
"""
    content = re.sub(r'(app\s*=\s*Flask\(__name__\))', r'\1\n' + cors_setup, content)

    # Replace include_router with register_blueprint
    def replace_include(match):
        line = match.group(0)
        parts = re.search(r'app\.include_router\((\w+)\.router', line)
        if parts:
            module = parts.group(1)
            prefix_match = re.search(r'prefix\s*=\s*"([^"]+)"', line)
            prefix = prefix_match.group(1) if prefix_match else ""
            new_line = f"app.register_blueprint({module}.bp, url_prefix=\"{prefix}\")"
            return new_line
        return line

    content = re.sub(r'app\.include_router\([^)]+\)', replace_include, content)
    return content


def process_file(input_path: Path, output_path: Path) -> None:
    """Transform a single Python file."""
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    content = transform_imports(content)
    content = transform_router_to_blueprint(content, input_path)
    content = transform_decorators(content)
    content = transform_path_params(content)
    content = transform_dependencies(content)
    content = transform_async(content)
    content = transform_exceptions(content)
    content = transform_response_model(content)

    # Special for main.py
    if input_path.name == "main.py":
        content = transform_main_py(content)

    # Also update model imports: from .. import models -> from ..models import ModelName
    # We'll do a simple replacement: replace "from .. import models" with "from ..models import *"
    # But better: we'll handle in each file. We'll leave as is; the __init__.py will allow importing.
    # However, we can replace "models." with "models." (no change) but ensure import.
    # We'll replace "from .. import models" with "from ..models import *"
    content = re.sub(r'from \.\. import models', 'from ..models import *', content)
    content = re.sub(r'from \.\. import schemas', 'from ..schemas import *', content)
    # Also handle direct references: models.User -> User (if imported)
    # Not doing that now.

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


def copy_non_python_files(src_dir: Path, dst_dir: Path) -> None:
    """Copy non-Python files."""
    for item in src_dir.rglob('*'):
        if item.is_file() and item.suffix != PYTHON_EXT:
            rel_path = item.relative_to(src_dir)
            dst_file = dst_dir / rel_path
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dst_file)
            print(f"Copied: {rel_path}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("ENHANCED FASTAPI → FLASK CONVERTER WITH SPLIT MODELS/SCHEMAS")
    print("=" * 70)

    if not SOURCE_DIR.exists():
        print(f"ERROR: Source directory '{SOURCE_DIR}' not found.")
        return

    # Clean output
    if OUTPUT_DIR.exists():
        print(f"Removing existing output directory: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)

    # Step 1: Split models and schemas
    models_path = SOURCE_DIR / "models.py"
    schemas_path = SOURCE_DIR / "schemas.py"
    if not models_path.exists():
        print("ERROR: models.py not found in source.")
        return
    if not schemas_path.exists():
        print("ERROR: schemas.py not found in source.")
        return

    print("\n[1] Splitting models.py into individual files...")
    model_names = split_models(models_path, OUTPUT_DIR)
    print(f"    Created {len(model_names)} model files.")

    print("\n[2] Splitting schemas.py into individual files...")
    schema_names = split_schemas(schemas_path, OUTPUT_DIR)
    print(f"    Created {len(schema_names)} schema files.")

    # Step 2: Convert all other Python files (routes, main, auth, database, etc.)
    print("\n[3] Converting route files and other modules...")
    for py_file in SOURCE_DIR.rglob(f"*{PYTHON_EXT}"):
        # Skip models.py and schemas.py since we already processed them (and we don't want them in the output)
        if py_file.name in ("models.py", "schemas.py"):
            continue
        # Also skip if in excluded dirs
        if any(part in EXCLUDED_DIRS for part in py_file.parts):
            continue
        rel_path = py_file.relative_to(SOURCE_DIR)
        output_file = OUTPUT_DIR / rel_path
        process_file(py_file, output_file)

    # Copy non-Python files (assets, etc.)
    print("\n[4] Copying static assets and other non-Python files...")
    copy_non_python_files(SOURCE_DIR, OUTPUT_DIR)

    # Step 5: Create a new requirements.txt
    req_file = OUTPUT_DIR / "requirements.txt"
    with open(req_file, 'w') as f:
        f.write("""# Flask requirements
Flask==2.3.3
Flask-CORS==4.0.1
Flask-JWT-Extended==4.5.3
Flask-SQLAlchemy==3.1.1
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pydantic==2.5.0
email-validator==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
""")
    print(f"    Created {req_file}")

    # Create a README
    readme = OUTPUT_DIR / "README.md"
    with open(readme, 'w') as f:
        f.write("# Flask Backend Converted from FastAPI\n")
        f.write("This backend was automatically converted from a FastAPI project to Flask.\n")
        f.write("Please review the code and adjust as necessary.\n")