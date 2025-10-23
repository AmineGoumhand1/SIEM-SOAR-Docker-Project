#!/usr/bin/env python3
import requests
import base64
import json

# === Configuration ===
BASE_URL = "http://localhost:9000"
ADMIN_EMAIL = "admin@thehive.local"
ADMIN_PASSWORD = "secret"

ENDPOINTS = {
	"organizations": "/api/v1/organisation",  # NOTE: British spelling!
	"users": "/api/v1/user"
}


# === Helpers ===
def make_basic_auth_header(username, password):
	"""
	Build Basic Auth header for TheHive.
	"""
	token = base64.b64encode(f"{username}:{password}".encode()).decode()
	return {"Authorization": f"Basic {token}", "Content-Type": "application/json"}


def make_request(method, endpoint, data=None):
	"""
	Generic Basic Auth request handler.
	"""
	headers = make_basic_auth_header(ADMIN_EMAIL, ADMIN_PASSWORD)
	url = f"{BASE_URL}{endpoint}"

	try:
		if method == "GET":
			response = requests.get(url, headers=headers)
		elif method == "POST":
			response = requests.post(url, headers=headers, json=data)
		elif method == "PATCH":
			response = requests.patch(url, headers=headers, json=data)
		else:
			raise ValueError(f"Unsupported HTTP method: {method}")

		return response
	except requests.exceptions.RequestException as e:
		print(f"❌ Request error: {e}")
		return None


def create_organisation(name, description):
	print(f"\n🏢 Creating organisation: {name}...")
	data = {
		"name": name,
		"description": description,
		"taskRule": "default",         # required field
		"observableRule": "default",   # required field
		"locked": False
	}

	response = make_request("POST", ENDPOINTS["organizations"], data)
	if response is None:
		print("❌ No response received.")
		return None

	if response.status_code == 201:
		org = response.json()
		print(f"✅ Organisation '{name}' created successfully (ID: {org.get('_id')})")
		return org
	elif response.status_code == 400:
		print(f"⚠️ Bad Request: {response.json().get('message')}")
		print(f"Response: {response.text}")
	elif response.status_code == 401:
		print("🚫 Unauthorized (check credentials)")
		print(f"Response: {response.text}")
	elif response.status_code == 403:
		print("🚫 Forbidden (insufficient permissions)")
		print(f"Response: {response.text}")
	else:
		print(f"❌ Error creating organisation: {response.status_code} - {response.text}")
	return None


# === User Creation (Org Admin) ===
def create_org_admin(org_id, username, user_email, display_name):
	print(f"\n👤 Creating admin user '{username}' in org '{org_id}'...")
	data = {
		"login": username,
		"name": display_name,
		"email": user_email,
		"organisation": org_id,
		"profile": "org-admin",
		"roles": ["read", "analyze", "orgadmin"],
		"password": "TempPassword123!",
		"status": "Active"
	}

	response = make_request("POST", ENDPOINTS["users"], data)
	if response is None:
		print("❌ No response received.")
		return None

	if response.status_code == 201:
		user = response.json()
		print(f"✅ Admin user '{username}' created successfully (ID: {user.get('_id')})")
		return user
	else:
		print(f"❌ Failed to create admin: {response.status_code} - {response.text}")
		return None
def print_manual_configuration_guide():
    print("\n" + "=" * 80)
    print("MANUAL CONFIGURATION GUIDE: CONNECTING CORTEX AND MISP TO THEHIVE")
    print("=" * 80)
    print("""
After running this script, open TheHive’s web interface and follow these steps:

[1] --- CONFIGURE CORTEX ---
  • Go to:  Administration → Cortex → Add Instance
  • Fill in:
      Name: cortex
      URL: http://cortex:9001
      Key: <Cortex API key>
      Check 'Active' and 'Check connectivity'
  • Click "Save"
  • Then go to:  Organisation → Config → Analyzers
    → Sync analyzers from Cortex

[2] --- CONFIGURE MISP ---
  • Go to:  Administration → MISP → Add Instance
  • Fill in:
      Name: misp
      URL: http://misp:8080
      Key: <MISP API key>
      SSL: Unchecked (if self-signed)
      Check connectivity before saving.
  • Click "Save"

[3] --- TEST INTEGRATION ---
  • In TheHive, create a case → Add observable (hash, domain, etc.)
  • Run analyzers from Cortex menu.
  • Check if MISP synchronization works.

Tip: If Cortex or MISP are in Docker, use their service names as hostnames (e.g., 'http://cortex:9001')
""")
    print("=" * 80)
    print("✅  TheHive is ready — now complete the setup from the GUI above!")
    print("=" * 80 + "\n")


# === Main Function ===
def main():
	# Create an organization
	org_name = "SOC"
	org_description = "This is an example organization."
	organization = create_organisation(org_name, org_description)

	if organization:
		org_id = organization.get("_id")

		# Create an admin user for the organization
		admin_username = "exampleadmin"
		admin_email = "admin@example.org"
		admin_display_name = "Example Admin"
		create_org_admin(org_id, admin_username, admin_email, admin_display_name)
	print_manual_configuration_guide()

if __name__ == "__main__":
	main()
