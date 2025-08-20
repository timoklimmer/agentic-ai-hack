import os
import json
from typing import Annotated
from semantic_kernel.functions import kernel_function

class CosmosDBPlugin:
    """
    A production-ready Cosmos DB plugin that connects to real Azure Cosmos DB.
    This plugin retrieves actual JSON documents from your database.
    """
    
    def __init__(self, endpoint: str = None, key: str = None, database_name: str = "MyDatabase", container_name: str = "MyContainer"):
        """
        Initialize the Cosmos DB plugin with connection details.
        For production, use environment variables or Azure Key Vault for credentials.
        """
        self.endpoint = endpoint or os.environ.get("COSMOS_ENDPOINT")
        self.key = key or os.environ.get("COSMOS_KEY") 
        self.database_name = "insurance_claims"
        self.container_name = "crash_reports"
    
    def _get_cosmos_client(self):
        """Create and return a Cosmos DB client."""
        if not self.endpoint or not self.key:
            raise Exception("Cosmos DB endpoint and key must be configured. Please set COSMOS_ENDPOINT and COSMOS_KEY environment variables.")
        
        try:
            from azure.cosmos import CosmosClient
            return CosmosClient(self.endpoint, self.key)
        except ImportError:
            raise ImportError("azure-cosmos package not installed. Run: pip install azure-cosmos")
        except Exception as e:
            raise Exception(f"Failed to create Cosmos DB client: {str(e)}")
    
    @kernel_function(description="Test Cosmos DB connection and list available claims")
    def test_connection(self) -> Annotated[str, "Connection test result and available claims"]:
        """Test the Cosmos DB connection and show what claims are available."""
        try:
            client = self._get_cosmos_client()
            database = client.get_database_client(self.database_name)
            container = database.get_container_client(self.container_name)
            
            # Test with a simple query to get all claim IDs
            query = "SELECT c.claim_id, c.id FROM c"
            items = list(container.query_items(
                query=query,
                enable_cross_partition_query=True,
                max_item_count=10  # Limit to first 10 for testing
            ))
            
            if items:
                claim_ids = [item.get('claim_id', item.get('id', 'Unknown')) for item in items]
                return f"✅ Cosmos DB connection successful! Found {len(items)} claims. Available claim IDs: {', '.join(claim_ids[:5])}{'...' if len(claim_ids) > 5 else ''}"
            else:
                return "✅ Cosmos DB connection successful, but no claims found in the container."
                
        except Exception as e:
            return f"❌ Cosmos DB connection failed: {str(e)}"
    
    @kernel_function(description="Get all documents from the Cosmos DB container")
    def get_all_documents(self) -> Annotated[str, "All documents from the container"]:
        """Retrieve all documents from the Cosmos DB container."""
        try:
            client = self._get_cosmos_client()
            database = client.get_database_client(self.database_name)
            container = database.get_container_client(self.container_name)
            
            # Query all documents
            query = "SELECT * FROM c"
            items = list(container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            if items:
                return json.dumps(items, indent=2, default=str)
            else:
                return "No documents found in the container."
                
        except Exception as e:
            return f"Error retrieving documents: {str(e)}"
    
    @kernel_function(description="Get a specific document by claim_id")
    def get_document_by_claim_id(
        self, 
        claim_id: Annotated[str, "The claim_id to search for"]
    ) -> Annotated[str, "Document data for the specified claim_id"]:
        """Retrieve a specific document by its claim_id."""
        try:
            client = self._get_cosmos_client()
            database = client.get_database_client(self.database_name)
            container = database.get_container_client(self.container_name)
            
            # Query for specific claim_id
            query = "SELECT * FROM c WHERE c.claim_id = @claim_id"
            parameters = [{"name": "@claim_id", "value": claim_id}]
            
            items = list(container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            if items:
                # Return the first matching document
                return json.dumps(items[0], indent=2, default=str)
            else:
                return f"No document found with claim_id: {claim_id}"
                
        except Exception as e:
            return f"Error retrieving document: {str(e)}"
    
    @kernel_function(description="Search documents by any field and value")
    def search_documents(
        self, 
        field_name: Annotated[str, "The field name to search in"],
        field_value: Annotated[str, "The value to search for"]
    ) -> Annotated[str, "Matching documents"]:
        """Search for documents where a specific field matches a value."""
        try:
            client = self._get_cosmos_client()
            database = client.get_database_client(self.database_name)
            container = database.get_container_client(self.container_name)
            
            # Dynamic query construction
            query = f"SELECT * FROM c WHERE c.{field_name} = @field_value"
            parameters = [{"name": "@field_value", "value": field_value}]
            
            items = list(container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            if items:
                return json.dumps(items, indent=2, default=str)
            else:
                return f"No documents found where {field_name} = {field_value}"
                
        except Exception as e:
            return f"Error searching documents: {str(e)}"
    
    @kernel_function(description="Get document statistics and summary")
    def get_container_stats(self) -> Annotated[str, "Container statistics and summary"]:
        """Get basic statistics about the container."""
        try:
            client = self._get_cosmos_client()
            database = client.get_database_client(self.database_name)
            container = database.get_container_client(self.container_name)
            
            # Get count and sample of documents
            count_query = "SELECT VALUE COUNT(1) FROM c"
            count_result = list(container.query_items(
                query=count_query,
                enable_cross_partition_query=True
            ))
            
            sample_query = "SELECT TOP 3 * FROM c"
            sample_items = list(container.query_items(
                query=sample_query,
                enable_cross_partition_query=True
            ))
            
            total_count = count_result[0] if count_result else 0
            
            stats = {
                "container_name": self.container_name,
                "database_name": self.database_name,
                "total_documents": total_count,
                "sample_documents": sample_items
            }
            
            return json.dumps(stats, indent=2, default=str)
            
        except Exception as e:
            return f"Error getting container stats: {str(e)}"
