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


def connect_to_weaviate() -> WeaviateClient:
    client = weaviate.connect_to_local(
        port=8080,
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
    if company_filter:
        company_filter_obj = Filter.by_property("company_author").like(company_filter)
    else:
        company_filter_obj = None

    if search_type == "Hybrid":
        alpha = 0.5
    elif search_type == "Vector":
        alpha = 1
    elif search_type == "Keyword":
        alpha = 0


    if rag_query:
        search_response = collection.generate.hybrid(
            query=query,
            target_vector="text_with_metadata",
            filters=company_filter_obj,
            alpha=alpha,
            limit=limit,
            grouped_task=rag_query
        )
    else:
        search_response = collection.query.hybrid(
            query=query,
            target_vector="text_with_metadata",
            filters=company_filter_obj,
            alpha=alpha,
            limit=limit,
        )
    return search_response


def get_pprof_results() -> str:
    return subprocess.run(
        ["go", "tool", "pprof", "-top", "http://localhost:6060/debug/pprof/heap"],
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
