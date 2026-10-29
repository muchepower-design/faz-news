
from pathlib import Path

# Root project directory
root = Path("shop")

# All directories to create
directories = [
    "src",
    "src/components",
    "src/context",
    "src/layouts",
    "src/pages",
]

# All empty files to create
files = [
    ".env",
    ".env.production",
    ".gitignore",
    "index.html",
    "package.json",
    "postcss.config.js",
    "tailwind.config.js",
    "vite.config.js",
    "src/main.jsx",
    "src/App.jsx",
    "src/index.css",
    "src/api.js",
    "src/components/ui.jsx",
    "src/context/AuthContext.jsx",
    "src/layouts/MainLayout.jsx",
    "src/pages/Home.jsx",
    "src/pages/Browse.jsx",
    "src/pages/VendorPage.jsx",
    "src/pages/AdvertDetail.jsx",
    "src/pages/Checkout.jsx",
    "src/pages/PaymentPage.jsx",
    "src/pages/OrderTracking.jsx",
    "src/pages/MyOrders.jsx",
    "src/pages/Login.jsx",
    "src/pages/Register.jsx",
]

# Create directories
for directory in directories:
    (root / directory).mkdir(parents=True, exist_ok=True)

# Create empty files without overwriting existing content
for file in files:
    file_path = root / file
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if not file_path.exists():
        file_path.touch()

print(f"Project structure created successfully at: {root.resolve()}")
print(f"Directories created: {len(directories) + 1}")
print(f"Files listed: {len(files)}")
