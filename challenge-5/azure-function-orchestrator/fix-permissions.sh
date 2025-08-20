#!/bin/bash

# ⚠️  DEPRECATED: This script is deprecated as of 2025-08-03
# 
# The functionality provided by this script has been integrated into the 
# Azure deployment templates in challenge-0/iac/. Use the new approach instead:
#
# RECOMMENDED APPROACH:
# 1. Deploy infrastructure with service principal permissions included:
#    cd ../../challenge-0/iac
#    ./deploy.sh -g rg-hack -s "3b442f77-79d6-4e66-8ba0-aaa486723d51"
#
# 2. Or use Azure CLI with the new templates:
#    az deployment group create \
#      --resource-group rg-hack \
#      --template-file azuredeploy.bicep \
#      --parameters servicePrincipalClientId="3b442f77-79d6-4e66-8ba0-aaa486723d51"
#
# For migration instructions, see: challenge-0/iac/SERVICE_PRINCIPAL_PERMISSIONS.md
#
# This script will be removed in a future version.

echo "⚠️  WARNING: This script is DEPRECATED!"
echo ""
echo "🔄 The functionality of this script has been moved to the infrastructure deployment templates."
echo "   Please use the new approach documented in:"
echo "   📖 challenge-0/iac/SERVICE_PRINCIPAL_PERMISSIONS.md"
echo ""
echo "✅ Recommended approach:"
echo "   cd ../../challenge-0/iac"
echo "   ./deploy.sh -g rg-hack -s \"3b442f77-79d6-4e66-8ba0-aaa486723d51\""
echo ""
echo "❓ Continue with deprecated script? (y/N)"
read -r response

if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "🚫 Execution cancelled. Please use the new deployment approach."
    exit 0
fi

echo ""
echo "⚠️  Proceeding with deprecated script..."
echo "   Consider migrating to the new approach for future deployments."
echo ""

# Original script content below this line
# ===================================================================

# Script to fix Azure AI Foundry permissions for the service principal

# Set variables from your local.settings.json
CLIENT_ID="3b442f77-79d6-4e66-8ba0-aaa486723d51"
TENANT_ID="1ff39846-6d88-4785-a285-5cac88f262b6"
AI_FOUNDRY_ENDPOINT="https://msagthack-aifoundry-k6hitc3c2ejg4.services.ai.azure.com/api/projects/msagthack-aiproject-k6hitc3c2ejg4"

# Extract resource group and AI service name from the endpoint
# Based on the Azure CLI output
RESOURCE_GROUP="rg-hack"
AI_SERVICE_NAME="msagthack-aifoundry-k6hitc3c2ejg4"

echo "🔐 Granting permissions to service principal..."
echo "Client ID: $CLIENT_ID"
echo "Resource Group: $RESOURCE_GROUP"
echo "AI Service: $AI_SERVICE_NAME"

# Grant "Cognitive Services User" role to the service principal
echo "📝 Assigning 'Cognitive Services User' role..."
az role assignment create \
    --role "Cognitive Services User" \
    --assignee "$CLIENT_ID" \
    --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.CognitiveServices/accounts/$AI_SERVICE_NAME"

# Also try "AI Developer" role if available
echo "📝 Assigning 'AI Developer' role..."
az role assignment create \
    --role "AI Developer" \
    --assignee "$CLIENT_ID" \
    --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.CognitiveServices/accounts/$AI_SERVICE_NAME" 2>/dev/null || echo "AI Developer role not found, skipping..."

# Grant "Contributor" role as a fallback
echo "📝 Assigning 'Contributor' role as fallback..."
az role assignment create \
    --role "Contributor" \
    --assignee "$CLIENT_ID" \
    --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.CognitiveServices/accounts/$AI_SERVICE_NAME"

echo "✅ Permissions granted! Wait a few minutes for permissions to propagate."
echo ""
echo "To verify permissions, run:"
echo "az role assignment list --assignee $CLIENT_ID --scope /subscriptions/\$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.CognitiveServices/accounts/$AI_SERVICE_NAME"
