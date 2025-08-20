# Deprecation Notice: fix-permissions.sh

## Status: ⚠️ DEPRECATED

**Effective Date:** August 3, 2025

## What happened?

The `fix-permissions.sh` script has been **deprecated** and its functionality has been integrated directly into the Azure deployment templates located in `challenge-0/iac/`.

## Why was this changed?

1. **Infrastructure as Code**: Permissions are now managed alongside infrastructure deployment
2. **Consistency**: All Azure resources and their permissions are configured in one place
3. **Automation**: No manual post-deployment steps required
4. **Version Control**: Permission changes are tracked in source control
5. **Reproducibility**: Deployments are now fully repeatable without manual intervention

## Migration Path

### Old Approach (Deprecated)
```bash
# Deploy infrastructure first
az deployment group create --resource-group rg-hack --template-file azuredeploy.bicep

# Then manually run permissions script
cd challenge-5/azure-function-orchestrator
./fix-permissions.sh
```

### New Approach (Recommended)
```bash
# Deploy infrastructure with permissions in one step
cd challenge-0/iac
./deploy.sh -g rg-hack -s "3b442f77-79d6-4e66-8ba0-aaa486723d51"
```

## Documentation

For detailed instructions on the new approach, see:
- [challenge-0/iac/SERVICE_PRINCIPAL_PERMISSIONS.md](../../challenge-0/iac/SERVICE_PRINCIPAL_PERMISSIONS.md)
- [challenge-0/README.md](../../challenge-0/README.md)

## Timeline

- **Now**: Script is deprecated but still functional (with warning messages)
- **Future Version**: Script will be removed entirely

## Need Help?

If you have questions about migrating to the new approach, please refer to the documentation or ask your coach during the hackathon.
