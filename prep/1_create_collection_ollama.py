# File: ./1_create_collection.py
from weaviate.classes.config import Property, DataType, Configure
from helpers import CollectionName, connect_to_weaviate


# Connect to Weaviate
client = connect_to_weaviate()  # Uses `weaviate.connect_to_local` under the hood

# Delete existing collection if it exists
client.collections.delete(CollectionName.SUPPORTCHAT)

default_vindex_config = Configure.VectorIndex.hnsw(
    # quantizer=Configure.VectorIndex.Quantizer.bq()
    # quantizer=Configure.VectorIndex.Quantizer.sq(training_limit=25000)
    # quantizer=Configure.VectorIndex.Quantizer.pq(training_limit=25000)
)

# Create a new collection with specified properties and vectorizer configuration
collection = client.collections.create(
    name=CollectionName.SUPPORTCHAT,
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
    # # ================================================================================
    # # Alternative: Set up the collection to use OpenAI
    # # ================================================================================
    # vectorizer_config=[
    #     Configure.NamedVectors.text2vec_openai(
    #         name="text",
    #         source_properties=["text"],
    #         vector_index_config=default_vindex_config,
    #         model="text-embedding-3-small",
    #     ),
    #     Configure.NamedVectors.text2vec_openai(
    #         name="text_with_metadata",
    #         source_properties=["text", "company_author"],
    #         vector_index_config=default_vindex_config,
    #         model="text-embedding-3-small",
    #     ),
    # ],
    # generative_config=Configure.Generative.openai(
    #     model="gpt-3.5-turbo-16k"
    # ),
    # # ================================================================================
    # # END: OpenAI configuration
    # # ================================================================================
    # # ================================================================================
    # # Alternative: Set up the collection to use Cohere
    # # ================================================================================
    # vectorizer_config=[
    #     Configure.NamedVectors.text2vec_cohere(
    #         name="text",
    #         source_properties=["text"],
    #         vector_index_config=default_vindex_config,
    #         model="embed-multilingual-light-v3.0",
    #     ),
    #     Configure.NamedVectors.text2vec_cohere(
    #         name="text_with_metadata",
    #         source_properties=["text", "company_author"],
    #         vector_index_config=default_vindex_config,
    #         model="embed-multilingual-light-v3.0",
    #     ),
    # ],
    # generative_config=Configure.Generative.cohere(model="command-r"),
    # # ================================================================================
    # # END: Cohere configuration
    # # ================================================================================
)

assert client.collections.exists(CollectionName.SUPPORTCHAT)

client.close()
