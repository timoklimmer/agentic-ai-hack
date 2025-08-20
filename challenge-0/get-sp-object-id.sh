#!/bin/bash

# Helper script to get the service principal object ID for Azure deployment
# This is needed for the optional service principal permissions in Challenge 5

echo "🔍 Getting service principal Object ID for Azure deployment..."
echo ""

# Check if user is logged in to Azure CLI
if ! az account show &> /dev/null; then
    echo "❌ You are not logged in to Azure CLI"
    echo "Please run: az login"
    exit 1
fi

# Check if CLIENT_ID is provided as argument or environment variable
CLIENT_ID="$1"
if [[ -z "$CLIENT_ID" ]]; then
    CLIENT_ID="${SERVICE_PRINCIPAL_CLIENT_ID}"
fi

# If still no CLIENT_ID, provide guidance
if [[ -z "$CLIENT_ID" ]]; then
    echo "❌ No service principal Client ID provided."
    echo ""
    echo "📋 Usage options:"
    echo "1. Pass Client ID as argument:"
    echo "   ./get-sp-object-id.sh <CLIENT_ID>"
    echo ""
    echo "2. Set environment variable:"
    echo "   export SERVICE_PRINCIPAL_CLIENT_ID=<CLIENT_ID>"
    echo "   ./get-sp-object-id.sh"
    echo ""
    echo "💡 If you don't have a service principal or don't need these permissions,"
    echo "   you can skip this step and leave the 'servicePrincipalObjectId' parameter"
    echo "   empty during Azure deployment."
    echo ""
    echo "📚 To create a new service principal, run:"
    echo "   az ad sp create-for-rbac --name \"my-hackathon-sp\" --query \"appId\" -o tsv"
    exit 1
fi

# Get the object ID
echo "🔍 Looking up service principal with Client ID: $CLIENT_ID"
OBJECT_ID=$(az ad sp show --id "$CLIENT_ID" --query "id" --output tsv 2>/dev/null)

if [[ -z "$OBJECT_ID" ]]; then
    echo "❌ Error: Could not find service principal with client ID: $CLIENT_ID"
    echo ""
    echo "   This might mean:"
    echo "   • You don't have permission to view this service principal"
    echo "   • The service principal doesn't exist in your tenant"
    echo "   • You're connected to the wrong Azure tenant"
    echo "   • The Client ID is incorrect"
    echo ""
    echo "🔍 Troubleshooting steps:"
    echo "1. Verify you're in the correct tenant:"
    echo "   az account show --query 'tenantId' -o tsv"
    echo ""
    echo "2. List service principals you have access to:"
    echo "   az ad sp list --display-name 'your-sp-name' --query '[].{DisplayName:displayName, AppId:appId, ObjectId:id}' -o table"
    echo ""
    echo "3. Create a new service principal if needed:"
    echo "   az ad sp create-for-rbac --name 'my-hackathon-sp'"
    echo ""
    echo "💡 If you don't need service principal permissions for Challenge 5,"
    echo "   you can deploy without this parameter (leave it empty)."
    exit 1
fi

echo "✅ Service Principal Object ID: $OBJECT_ID"
echo "✅ Service Principal Client ID: $CLIENT_ID"
echo ""
echo "📋 Next steps:"
echo "1. Copy the Object ID above: $OBJECT_ID"
echo "2. Use the 'Deploy to Azure' button in the README"
echo "3. Paste this Object ID into the 'servicePrincipalObjectId' parameter"
echo "4. Complete the deployment"
echo ""
echo "💡 Or leave the parameter empty if you don't need service principal permissions."
