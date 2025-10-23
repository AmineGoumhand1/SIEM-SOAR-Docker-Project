#!/usr/bin/env python3
import requests
import json

# -----------------------
# CONFIGURATION
# -----------------------
CORTEX_URL = "http://10.0.2.9:9001"  # Your Cortex URL
SUPERADMIN_API_KEY = "QjyqKncjvhb0wDb4K7kOJ8tkxpJ5owkR"
ORG_NAME = "SOC-Final"
ORG_DESC = "SOC Organization"
ORGADMIN_LOGIN = "socadmin@cortex.com"
ORGADMIN_NAME = "SOC Admin"
ORGADMIN_PASSWORD = "StrongPassword123"

HEADERS = {
    "Authorization": f"Bearer {SUPERADMIN_API_KEY}",
    "Content-Type": "application/json"
}

# -----------------------
# HELPER FUNCTIONS
# -----------------------
def create_organization():
    url = f"{CORTEX_URL}/api/organization"
    payload = {
        "name": ORG_NAME,
        "description": ORG_DESC,
        "status": "Active"
    }
    response = requests.post(url, headers=HEADERS, data=json.dumps(payload), verify=False)
    if response.status_code == 201 or response.status_code == 200:
        print(f"✅ Organization '{ORG_NAME}' created successfully.")
        return True
    elif response.status_code == 409:
        print(f"⚠️ Organization '{ORG_NAME}' already exists.")
        return True
    else:
        print(f"❌ Failed to create organization: {response.status_code} {response.text}")
        return False

def create_orgadmin_user():
    url = f"{CORTEX_URL}/api/user"
    payload = {
        "name": ORGADMIN_NAME,
        "roles": ["read", "analyze", "orgadmin"],
        "organization": ORG_NAME,
        "login": ORGADMIN_LOGIN
    }
    response = requests.post(url, headers=HEADERS, data=json.dumps(payload), verify=False)
    if response.status_code == 201 or response.status_code == 200:
        print(f"✅ User '{ORGADMIN_LOGIN}' created successfully.")
        return True
    elif response.status_code == 409:
        print(f"⚠️ User '{ORGADMIN_LOGIN}' already exists.")
        return True
    else:
        print(f"❌ Failed to create user: {response.status_code} {response.text}")
        return False

def set_user_password():
    url = f"{CORTEX_URL}/api/user/{ORGADMIN_LOGIN}/password/set"
    payload = {"password": ORGADMIN_PASSWORD}
    response = requests.post(url, headers=HEADERS, data=json.dumps(payload), verify=False)
    if response.status_code == 204:
        print(f"✅ Password for user '{ORGADMIN_LOGIN}' set successfully.")
        return True
    else:
        print(f"❌ Failed to set password: {response.status_code} {response.text}")
        return False

# -----------------------
# MAIN SCRIPT
# -----------------------
if __name__ == "__main__":
    print("=== Cortex 2 Automated Setup ===")
    
    if create_organization():
        if create_orgadmin_user():
            set_user_password()
