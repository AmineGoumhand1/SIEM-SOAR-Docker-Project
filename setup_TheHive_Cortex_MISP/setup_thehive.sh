#!/usr/bin/env bash
set +e  # Do NOT exit on errors

# === Configuration ===
THEHIVE_URL="http://localhost:9000"
ORG_JSON_FILE="org.json"
USER_LOGIN="exampleadmin@soc.local"
USER_NAME="Example Admin"
USER_PASS="TempPassword123!"
AUTH_HEADER="V8XQ+IF8Dyo1SVGO2/4y8FhmmGQ8aMGu"  # Your TheHive API key

ORG_NAME="SOC"

# Step 1: Check if org ID exists in JSON
if [ -f "$ORG_JSON_FILE" ]; then
    ORG_ID=$(jq -r '._id' "$ORG_JSON_FILE")
    echo "🔎 Loaded organisation ID from $ORG_JSON_FILE: $ORG_ID"
fi

# Step 2: If no ID, check on TheHive
if [ -z "$ORG_ID" ] || [ "$ORG_ID" == "null" ]; then
    echo "🔎 Checking if organisation '$ORG_NAME' exists on TheHive..."
    ORG_RESPONSE=$(curl -s -X GET "$THEHIVE_URL/api/v1/organisation" \
        -H "Authorization: Bearer $AUTH_HEADER" \
        -H "Content-Type: application/json")

    ORG_ID=$(echo "$ORG_RESPONSE" | jq -r --arg NAME "$ORG_NAME" '
        if type=="array" then map(select(.name==$NAME)) | .[0]._id
        else if .name==$NAME then ._id else empty end end
    ')

    if [ -z "$ORG_ID" ] || [ "$ORG_ID" == "null" ]; then
        # Create organisation
        echo "🏢 Creating organisation '$ORG_NAME'..."
        CREATE_RESP=$(curl -s -X POST "$THEHIVE_URL/api/v1/organisation" \
            -H "Authorization: Bearer $AUTH_HEADER" \
            -H "Content-Type: application/json" \
            -d "$(jq -n --arg name "$ORG_NAME" --arg desc "$ORG_NAME organization" '{name:$name, description:$desc, taskRule:"default", observableRule:"default", locked:false}')")

        ORG_ID=$(echo "$CREATE_RESP" | jq -r '._id')
        if [ -z "$ORG_ID" ] || [ "$ORG_ID" == "null" ]; then
            echo "❌ Warning: Failed to create organisation. Response:"
            echo "$CREATE_RESP" | jq .
        else
            echo "✅ Organisation created with ID: $ORG_ID"
        fi
    else
        echo "✅ Organisation already exists with ID: $ORG_ID"
    fi

    # Save org ID to JSON only if valid
    if [ -n "$ORG_ID" ] && [ "$ORG_ID" != "null" ]; then
        echo "{\"_id\":\"$ORG_ID\",\"name\":\"$ORG_NAME\"}" > "$ORG_JSON_FILE"
        echo "💾 Organisation ID saved to $ORG_JSON_FILE"
    fi
fi

# Step 3: Create user
if [ -n "$ORG_ID" ] && [ "$ORG_ID" != "null" ]; then
    echo "👤 Creating user '$USER_LOGIN' in org ID '$ORG_ID'..."
    USER_RESP=$(curl -s -X POST "$THEHIVE_URL/api/v1/user" \
        -H "Authorization: Bearer $AUTH_HEADER" \
        -H "Content-Type: application/json" \
        -d "$(jq -n --arg login "$USER_LOGIN" --arg name "$USER_NAME" --arg org "$ORG_ID" --arg pass "$USER_PASS" '{login:$login, name:$name, organisation:$org, profile:"org-admin", password:$pass, status:"Ok"}')")

    echo "$USER_RESP" | jq .
else
    echo "⚠️ Cannot create user: organisation ID is empty"
fi

echo "✅ Script finished."
