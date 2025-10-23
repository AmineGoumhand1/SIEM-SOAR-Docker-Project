#!/usr/bin/env python3
import requests
import json
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MISPManager:
    def __init__(self, base_url, api_key):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Authorization": api_key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def make_request(self, method, endpoint, data=None):
        """Make authenticated API request to MISP (self-signed SSL compatible)"""
        url = f"{self.base_url}{endpoint}"

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, verify=False)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=self.headers, verify=False)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers, verify=False)
            else:
                print(f"❌ Unsupported HTTP method: {method}")
                return None
            return response

        except Exception as e:
            print(f"❌ API request error: {e}")
            return None

    # ------------------- Organizations -------------------
    def list_organizations(self):
        """List all organizations in MISP"""
        print("\n📋 Listing all organizations...")
        response = self.make_request("GET", "/organisations")

        if response and response.status_code == 200:
            organizations = response.json()
            print(f"✅ Found {len(organizations)} organizations:")
            for org in organizations:
                org_data = org.get('Organisation', org)
                print(f"   - {org_data.get('name')} (ID: {org_data.get('id')}, Type: {org_data.get('type')})")
            return organizations
        else:
            status_code = response.status_code if response else "No response"
            print(f"❌ Failed to list organizations: {status_code}")
            if response:
                print(f"   Error details: {response.text}")
            return []

    def create_organization(self, name, description="", org_type="ORG", nationality="", sector=""):
        """Create a new organization in MISP"""
        print(f"\n🏢 Creating organization: {name}...")

        org_data = {
            "name": name,
            "description": description,
            "type": org_type,
            "nationality": nationality,
            "sector": sector
        }

        response = self.make_request("POST", "/admin/organisations/add", org_data)

        if response and response.status_code == 200:
            org_info = response.json()
            org_obj = org_info.get('Organisation', org_info)
            print(f"✅ Organization '{name}' created successfully!")
            print(f"   ID: {org_obj.get('id')}")
            print(f"   Type: {org_obj.get('type')}")
            return org_obj
        else:
            status_code = response.status_code if response else "No response"
            print(f"❌ Failed to create organization: {status_code}")
            if response:
                print(f"   Error details: {response.text}")
            return None

    # ------------------- Users -------------------
    def create_user(self, email, org_id, role_id=2, password=None, autoalert=True):
        """Create a new user in MISP"""
        print(f"\n👤 Creating user: {email}...")

        user_data = {
            "email": email,
            "org_id": org_id,
            "role_id": role_id,  # 3 = Org Admin, 1 = Site Admin
            "autoalert": autoalert,
            "contactalert": False,
            "disabled": False
        }

        response = self.make_request("POST", "/admin/users/add", user_data)

        if response and response.status_code == 200:
            user_info = response.json()
            user_obj = user_info.get('User', user_info)

            print(f"✅ User '{email}' created successfully!")
            print(f"   User ID: {user_obj.get('id')}")
            print(f"   Organization ID: {user_obj.get('org_id')}")
            print(f"   Role ID: {user_obj.get('role_id')}")

            # Set password if provided
            if password and user_obj.get('id'):
                self.set_user_password(user_obj['id'], password)

            return user_obj
        else:
            status_code = response.status_code if response else "No response"
            print(f"❌ Failed to create user: {status_code}")
            if response:
                print(f"   Error details: {response.text}")
            return None

    def set_user_password(self, user_id, password):
        """Set password for a user"""
        print(f"   🔐 Setting password for user ID: {user_id}...")

        password_data = {"password": password}

        response = self.make_request("POST", f"/admin/users/edit/{user_id}", password_data)

        if response and response.status_code == 200:
            print(f"   ✅ Password set successfully")
            return True
        else:
            print(f"   ⚠️  Password may need to be set manually or via different method")
            if response:
                print(f"   Error details: {response.text}")
            return False

    def list_users(self):
        """List all users in MISP"""
        print("\n👥 Listing all users...")
        response = self.make_request("GET", "/admin/users")

        if response and response.status_code == 200:
            users = response.json()
            print(f"✅ Found {len(users)} users:")
            for user in users:
                user_data = user.get('User', user)
                print(f"   - {user_data.get('email')} (Org ID: {user_data.get('org_id')}, Role: {user_data.get('role_id')})")
            return users
        else:
            status_code = response.status_code if response else "No response"
            print(f"❌ Failed to list users: {status_code}")
            return []

# ------------------- MAIN -------------------
def main():
    print("🚀 Starting MISP automated setup...")

    # Configuration - UPDATE THESE VALUES
    MISP_URL = "https://10.0.2.10"  # HTTPS server URL
    ADMIN_API_KEY = "YiUZidfWRYAJx9TnC0mftwHr4hiEy2egnAsJnWLB"  # Admin API key

    # Initialize MISP manager
    misp = MISPManager(MISP_URL, ADMIN_API_KEY)

    # Step 1: List existing organizations
    misp.list_organizations()

    # Step 2: Create a new organization
    new_org_name = "SOC"
    new_org_description = "Security operations team for Division A"

    new_org = misp.create_organization(
        name=new_org_name,
        description=new_org_description,
        org_type="ORG"  # "ORG" = regular org, "ADMIN" = admin org
    )

    if not new_org:
        print("❌ Organization creation failed. Exiting.")
        return

    org_id = new_org.get('id') or new_org.get('Organisation', {}).get('id')
    if not org_id:
        print("❌ Could not extract organization ID. Exiting.")
        return

    # Step 3: Create admin user for the new organization
    admin_email = "secadmin-a@company.com"
    admin_password = "TempPassword123!"  # Change after first login
    org_admin_role_id = 2  # Org Admin

    admin_user = misp.create_user(
        email=admin_email,
        org_id=org_id,
        role_id=org_admin_role_id,
        password=admin_password
    )

    # Step 4: List users to verify
    if admin_user:
        misp.list_users()

    print(f"\n🎉 MISP setup completed!")
    print(f"   Organization: {new_org_name} (ID: {org_id})")
    print(f"   Admin user: {admin_email}")
    if admin_user:
        print(f"   User ID: {admin_user.get('id')}")
    print(f"   Temporary password: {admin_password}")


if __name__ == "__main__":
    main()
