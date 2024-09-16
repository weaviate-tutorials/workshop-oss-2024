# File: ./helpers.py

from enum import Enum
from datasets import load_dataset
from datetime import datetime
from dateutil import parser
from typing import Dict, Union, List, Any, Literal, Optional
from collections.abc import Iterator
import claudette
from anthropic.types import Message
import ollama
import subprocess
import weaviate
from weaviate import WeaviateClient
from weaviate.collections import Collection
from weaviate.classes.query import Metrics, Filter
import os


class CollectionName(str, Enum):
    """Enum for Weaviate collection names."""

    SUPPORTCHAT = "SupportChat"
    SUPPORTCHAT_MT = "SupportChatMT"


def connect_to_weaviate() -> WeaviateClient:
    client = weaviate.connect_to_local(
        port=8080,
        # Passing headers in case we use these integrations
        headers={
            "X-ANTHROPIC-API-KEY": os.environ["ANTHROPIC_API_KEY"],
            "X-OPENAI-API-KEY": os.environ["OPENAI_API_KEY"],
            "X-COHERE-API-KEY": os.environ["COHERE_API_KEY"],
        },
    )
    return client


def connect_to_mt_weaviate() -> WeaviateClient:
    client = weaviate.connect_to_local(
        port=8180,
        grpc_port=50151,
        # Passing headers in case we use these integrations
        headers={
            "X-ANTHROPIC-API-KEY": os.environ["ANTHROPIC_API_KEY"],
            "X-OPENAI-API-KEY": os.environ["OPENAI_API_KEY"],
            "X-COHERE-API-KEY": os.environ["COHERE_API_KEY"],
        },
    )
    return client


def get_collection_names() -> List[str]:
    client = connect_to_weaviate()
    collections = client.collections.list_all(simple=True)
    return collections.keys()


def _parse_time(time_string: str) -> datetime:
    # Parse the string into a datetime object
    dt = parser.parse(time_string)
    return dt


def get_data_objects(
    max_text_length: int = 10**5,
) -> Iterator[Dict[str, Union[datetime, str, int]]]:
    ds = load_dataset("Rakuto/twitter_customer_support_dialogue")["train"]
    for item in ds:
        yield {
            "text": item["text"][:max_text_length],
            "dialogue_id": item["dialogue_id"],
            "company_author": item["company_author"],
            "created_at": _parse_time(item["created_at"]),
        }


def get_top_companies(collection: Collection):
    response = collection.aggregate.over_all(
        return_metrics=Metrics("company_author").text(
            top_occurrences_count=True, top_occurrences_value=True, count=True
        )
    )
    return response.properties["company_author"].top_occurrences


def weaviate_query(
    collection: Collection,
    query: str,
    company_filter: str,
    limit: int,
    search_type: Literal["Hybrid", "Vector", "Keyword"],
    rag_query: Optional[str] = None,
):
    # ================================================================================
    # STUDENT **TODO**:
    # Implement the `weaviate_query` function to query Weaviate.
    # ================================================================================
    if company_filter:
        # What does a filter look like for the company_author property?
        company_filter_obj = None
    else:
        company_filter_obj = None

    # What should alpha be for a hybrid, vector, or keyword search?
    if search_type == "Hybrid":
        alpha = 0
    elif search_type == "Vector":
        alpha = 0
    elif search_type == "Keyword":
        alpha = 0

    if not rag_query:
        # Implement the search query
        search_response = None
    else:
        # Implement the RAG query
        search_response = None
    # ================================================================================
    # If you need help with the query, check the hints/helpers.py file.
    # ================================================================================
    return search_response


def get_pprof_results(port=6060) -> str:
    return subprocess.run(
        ["go", "tool", "pprof", "-top", f"http://localhost:{port}/debug/pprof/heap"],
        capture_output=True,
        text=True,
        timeout=10,
    )


def manual_rag(
    rag_query: str, context: str, provider: Literal["claude", "ollama"]
) -> List[str]:
    prompt = f"""
    Answer this query <query>{rag_query}</query>
    about these conversations between
    customer support people and customers: {context}
    """
    if provider == "claude":
        chat = claudette.Chat(
            model="claude-3-haiku-20240307"  # e.g. "claude-3-haiku-20240307" or "claude-3-5-sonnet-20240620"
        )
        r: Message = chat(prompt)
        rag_responses = [c.text for c in r.content]
        return rag_responses
    elif provider == "ollama":
        response = ollama.chat(
            model="gemma2b:2b",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        return [(response["message"]["content"])]


STREAMLIT_STYLING = """
<style>
    .stHeader {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
</style>
"""
