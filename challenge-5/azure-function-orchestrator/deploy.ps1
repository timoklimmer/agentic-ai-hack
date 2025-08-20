# Azure Function Deployment Script
# This script helps deploy the Insurance Claim Orchestrator to Azure

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$true)]
    [string]$FunctionAppName,
    
    [Parameter(Mandatory=$true)]
    [string]$StorageAccountName,
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "West US 2",
    
    [Parameter(Mandatory=$false)]
    [string]$PythonVersion = "3.9"
)

Write-Host "🚀 Starting Azure Function deployment..." -ForegroundColor Green

# Check if Azure CLI is installed
if (!(Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Error "Azure CLI is not installed. Please install it first."
    exit 1
}

# Check if Functions Core Tools is installed  
if (!(Get-Command func -ErrorAction SilentlyContinue)) {
    Write-Error "Azure Functions Core Tools is not installed. Please install it first."
    exit 1
}

try {
    # Login to Azure (if not already logged in)
    Write-Host "🔐 Checking Azure login status..." -ForegroundColor Yellow
    $loginStatus = az account show 2>$null
    if (!$loginStatus) {
        Write-Host "Please login to Azure..."
        az login
    }

    # Create resource group if it doesn't exist
    Write-Host "📦 Creating resource group: $ResourceGroupName" -ForegroundColor Yellow
    az group create --name $ResourceGroupName --location $Location

    # Create storage account
    Write-Host "💾 Creating storage account: $StorageAccountName" -ForegroundColor Yellow
    az storage account create `
        --name $StorageAccountName `
        --location $Location `
        --resource-group $ResourceGroupName `
        --sku Standard_LRS

    # Create Function App
    Write-Host "⚡ Creating Function App: $FunctionAppName" -ForegroundColor Yellow
    az functionapp create `
        --resource-group $ResourceGroupName `
        --consumption-plan-location $Location `
        --runtime python `
        --runtime-version $PythonVersion `
        --functions-version 4 `
        --name $FunctionAppName `
        --storage-account $StorageAccountName

    # Configure application settings (you'll need to update appsettings.json first)
    Write-Host "⚙️ Configuring application settings..." -ForegroundColor Yellow
    if (Test-Path "appsettings.json") {
        Write-Host "Found appsettings.json - applying configuration..."
        az functionapp config appsettings set `
            --name $FunctionAppName `
            --resource-group $ResourceGroupName `
            --settings @appsettings.json
    } else {
        Write-Warning "appsettings.json not found. Please configure your environment variables manually."
    }

    # Deploy the function
    Write-Host "🚀 Deploying function to Azure..." -ForegroundColor Yellow
    func azure functionapp publish $FunctionAppName

    # Get the function URL
    $functionUrl = az functionapp show --name $FunctionAppName --resource-group $ResourceGroupName --query "defaultHostName" --output tsv
    
    Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔗 Function App URL: https://$functionUrl" -ForegroundColor Cyan
    Write-Host "🔗 Health Check: https://$functionUrl/api/health" -ForegroundColor Cyan
    Write-Host "🔗 Claim Processing: https://$functionUrl/api/claim" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 Next steps:" -ForegroundColor Yellow
    Write-Host "1. Update your appsettings.json with actual Azure resource endpoints"
    Write-Host "2. Test the health endpoint: https://$functionUrl/api/health"
    Write-Host "3. Test Cosmos DB connection: https://$functionUrl/api/test-cosmos"
    Write-Host "4. Process a test claim: POST to https://$functionUrl/api/claim"

} catch {
    Write-Error "❌ Deployment failed: $($_.Exception.Message)"
    exit 1
}

Write-Host "🎉 Azure Function deployment script completed!" -ForegroundColor Green
