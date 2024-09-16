# File: ./1_create_collection.py
from weaviate.classes.config import Property, DataType, Configure
from helpers import CollectionName, connect_to_weaviate


# Connect to Weaviate
client = connect_to_weaviate()  # Uses `weaviate.connect_to_local` under the hood

# Delete existing collection if it exists
client.collections.delete(CollectionName.SUPPORTCHAT_MT)

default_vindex_config = Configure.VectorIndex.hnsw(
    # quantizer=Configure.VectorIndex.Quantizer.bq()
    quantizer=Configure.VectorIndex.Quantizer.sq(training_limit=25000)
    # quantizer=Configure.VectorIndex.Quantizer.pq(training_limit=25000)
)

# Create a new collection with specified properties and vectorizer configuration
chunks = client.collections.create(
    name=CollectionName.SUPPORTCHAT_MT,
    multi_tenancy_config=Configure.multi_tenancy(enabled=True),
    properties=[
        Property(name="text", data_type=DataType.TEXT),
        Property(name="dialogue_id", data_type=DataType.INT),
        Property(name="company_author", data_type=DataType.TEXT),
        Property(name="created_at", data_type=DataType.DATE),
    ],
    # ================================================================================
    # Using our Ollama integration: https://weaviate.io/developers/weaviate/model-providers/ollama
    # Many other integrations available. See https://weaviate.io/developers/weaviate/model-providers/
    # ================================================================================
    vectorizer_config=[
        Configure.NamedVectors.text2vec_ollama(
            name="text",
            source_properties=["text"],
            vector_index_config=default_vindex_config,
            api_endpoint="http://host.docker.internal:11434",
            model="nomic-embed-text",
        ),
        Configure.NamedVectors.text2vec_ollama(
            name="text_with_metadata",
            source_properties=["text", "company_author"],
            vector_index_config=default_vindex_config,
            api_endpoint="http://host.docker.internal:11434",
            model="nomic-embed-text",
        ),
    ],
    generative_config=Configure.Generative.ollama(
        api_endpoint="http://host.docker.internal:11434", model="gemma2:2b"
    ),
    # ================================================================================
    # END: Ollama configuration
    # ================================================================================
)

assert client.collections.exists(CollectionName.SUPPORTCHAT_MT)

client.close()
