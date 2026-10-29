# save as test_login.py
import requests
r = requests.post("http://localhost:8000/api/token", 
                  data={"username": "admin", "password": "admin123"})
print(r.status_code, r.json())