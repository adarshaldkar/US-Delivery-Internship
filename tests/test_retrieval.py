"""
Unit tests for knowledge base retrieval engine.
"""

import pytest
from src.retrieval import KnowledgeBaseRetriever, kb_retriever


def test_kb_retriever_initialization():
    assert len(kb_retriever.chunks) > 0
    assert any(chunk.error_codes for chunk in kb_retriever.chunks)


def test_exact_error_code_retrieval():
    query = "We are receiving ERR_CONNECTION_TIMEOUT after 30s in DataBridge Pro pipeline."
    results = kb_retriever.search(query, top_k=3)
    assert len(results) > 0
    assert results[0].is_exact_error_match is True
    assert "databridge-pro.md" in results[0].chunk.document_path or "troubleshooting" in results[0].chunk.document_path


def test_lexical_search_without_error_code():
    query = "How do we configure SAML 2.0 single sign-on with Okta and Azure AD?"
    results = kb_retriever.search(query, top_k=3)
    assert len(results) > 0
    top_doc = results[0].chunk.document_path
    assert "authentication-sso.md" in top_doc or "securevault.md" in top_doc


def test_irrelevant_query_low_confidence():
    query = "What is the capital city of Australia?"
    results = kb_retriever.search(query, top_k=3)
    if results:
        assert results[0].score < 0.25
