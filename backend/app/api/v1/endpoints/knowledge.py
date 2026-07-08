"""
Nexora Platform — Knowledge Base & Document Management API Router Endpoints
"""

from __future__ import annotations

import uuid
from typing import Any
from fastapi import APIRouter, Depends, Request, Response, status, File, UploadFile, Form
from sqlalchemy import select

from app.api.deps import get_knowledge_service, get_document_service, get_current_user, get_current_organization
from app.models.user import User
from app.models.config import Organization
from app.models.knowledge import KnowledgeBase, Document, DocumentChunk
from app.schemas.base import ApiResponse
from app.schemas.knowledge import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    DocumentResponse,
    DocumentChunkResponse,
)
from app.services.knowledge import KnowledgeService, DocumentService

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base & Document Management"])


@router.get(
    "",
    response_model=ApiResponse[list[KnowledgeBaseResponse]],
    status_code=status.HTTP_200_OK,
    summary="List organization Knowledge Bases",
)
async def list_knowledge_bases(
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    kb_service: KnowledgeService = Depends(get_knowledge_service),
) -> dict:
    """
    Returns active Knowledge Bases scoped by organization tenant.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    kb_list = await kb_service.kb_repo.list_by_org(active_org.id)
    data = [KnowledgeBaseResponse.model_validate(kb) for kb in kb_list]
    return {
        "success": True,
        "message": "Knowledge Bases list retrieved successfully",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.post(
    "",
    response_model=ApiResponse[KnowledgeBaseResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Knowledge Base",
)
async def create_knowledge_base(
    payload: KnowledgeBaseCreate,
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    kb_service: KnowledgeService = Depends(get_knowledge_service),
) -> dict:
    """
    Registers a new Knowledge Base container per organization tenant.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    
    kb = await kb_service.create_knowledge_base(
        organization_id=active_org.id,
        name=payload.name,
        description=payload.description,
        category_id=payload.category_id,
    )

    data = KnowledgeBaseResponse.model_validate(kb)
    return {
        "success": True,
        "message": "Knowledge Base created successfully",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.get(
    "/{id}",
    response_model=ApiResponse[KnowledgeBaseResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Knowledge Base details",
)
async def get_knowledge_base(
    id: uuid.UUID,
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    kb_service: KnowledgeService = Depends(get_knowledge_service),
) -> dict:
    """
    Retrieves information on a specific Knowledge Base container.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    kb = await kb_service.kb_repo.get_by_id(id, active_org.id)
    if not kb or kb.is_archived:
        raise NotFoundException(message="Knowledge Base not found", error_code="KB_NOT_FOUND")

    data = KnowledgeBaseResponse.model_validate(kb)
    return {
        "success": True,
        "message": "Knowledge Base details retrieved",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.put(
    "/{id}",
    response_model=ApiResponse[KnowledgeBaseResponse],
    status_code=status.HTTP_200_OK,
    summary="Modify Knowledge Base configurations",
)
async def update_knowledge_base(
    id: uuid.UUID,
    payload: KnowledgeBaseUpdate,
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    kb_service: KnowledgeService = Depends(get_knowledge_service),
) -> dict:
    """
    Modifies Knowledge Base descriptions or category links.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    kb = await kb_service.kb_repo.get_by_id(id, active_org.id)
    if not kb or kb.is_archived:
        raise NotFoundException(message="Knowledge Base not found", error_code="KB_NOT_FOUND")

    if payload.name:
        kb.name = payload.name
    if payload.description:
        kb.description = payload.description
    if payload.category_id:
        kb.category_id = payload.category_id

    updated = await kb_service.kb_repo.update(kb)
    data = KnowledgeBaseResponse.model_validate(updated)
    return {
        "success": True,
        "message": "Knowledge Base configurations updated",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.delete(
    "/{id}",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Archive Knowledge Base",
)
async def delete_knowledge_base(
    id: uuid.UUID,
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    kb_service: KnowledgeService = Depends(get_knowledge_service),
) -> dict:
    """
    Soft-archives Knowledge Base container.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    kb = await kb_service.kb_repo.get_by_id(id, active_org.id)
    if not kb or kb.is_archived:
        raise NotFoundException(message="Knowledge Base not found", error_code="KB_NOT_FOUND")

    kb.is_archived = True
    await kb_service.kb_repo.update(kb)
    return {
        "success": True,
        "message": "Knowledge Base archived successfully",
        "data": None,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


# --- Documents Endpoints ---

@router.post(
    "/documents/upload",
    response_model=ApiResponse[DocumentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload and ingest a document",
)
async def upload_document(
    request: Request,
    knowledge_base_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    author: str | None = Form(None),
    chunk_size: int = Form(1000),
    overlap: int = Form(200),
    active_org: Organization = Depends(get_current_organization),
    doc_service: DocumentService = Depends(get_document_service),
) -> dict:
    """
    Ingests local text or binary document file and triggers chunk parsing queues.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    file_bytes = await file.read()
    
    doc = await doc_service.upload_document(
        organization_id=active_org.id,
        knowledge_base_id=knowledge_base_id,
        filename=file.filename,
        file_content=file_bytes,
        mime_type=file.content_type,
        author=author,
        custom_chunk_size=chunk_size,
        custom_overlap=overlap,
    )

    data = DocumentResponse.model_validate(doc)
    return {
        "success": True,
        "message": "Document uploaded and scheduled for parsing chunk splits",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.get(
    "/documents",
    response_model=ApiResponse[list[DocumentResponse]],
    status_code=status.HTTP_200_OK,
    summary="List organization documents",
)
async def list_documents(
    request: Request,
    knowledge_base_id: uuid.UUID | None = None,
    status: str | None = None,
    q: str | None = None,
    active_org: Organization = Depends(get_current_organization),
    doc_service: DocumentService = Depends(get_document_service),
) -> dict:
    """
    Returns files scoped to organization, support filters by KB and title keyword searches.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    docs = await doc_service.doc_repo.search_documents(
        organization_id=active_org.id,
        query_string=q,
        knowledge_base_id=knowledge_base_id,
        status=status,
    )
    data = [DocumentResponse.model_validate(d) for d in docs]
    return {
        "success": True,
        "message": "Documents retrieved successfully",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.get(
    "/documents/{id}",
    response_model=ApiResponse[DocumentResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Document details with chunks",
)
async def get_document_details(
    id: uuid.UUID,
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    doc_service: DocumentService = Depends(get_document_service),
) -> dict:
    """
    Returns Document details with splits chunks.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    doc = await doc_service.doc_repo.get_by_id_scoped(id, active_org.id)
    if not doc:
        raise NotFoundException(message="Document not found", error_code="DOCUMENT_NOT_FOUND")

    data = DocumentResponse.model_validate(doc)
    return {
        "success": True,
        "message": "Document details resolved",
        "data": data,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.delete(
    "/documents/{id}",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Delete Document",
)
async def delete_document(
    id: uuid.UUID,
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    doc_service: DocumentService = Depends(get_document_service),
) -> dict:
    """
    Deletes raw file from storage and purges chunks relationships.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    doc = await doc_service.doc_repo.get_by_id_scoped(id, active_org.id)
    if not doc:
        raise NotFoundException(message="Document not found", error_code="DOCUMENT_NOT_FOUND")

    # Purge from Storage Provider
    await doc_service.storage.delete_file(doc.source_url)
    
    # Cascade delete ORM triggers database updates
    await doc_service.doc_repo.delete(doc.id, active_org.id)
    
    return {
        "success": True,
        "message": "Document purged successfully",
        "data": None,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }


@router.post(
    "/documents/{id}/reindex",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Reindex Document splits",
)
async def reindex_document(
    id: uuid.UUID,
    request: Request,
    active_org: Organization = Depends(get_current_organization),
    doc_service: DocumentService = Depends(get_document_service),
) -> dict:
    """
    Triggers re-extraction and splits generation.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    await doc_service.reindex_document(id, active_org.id)
    return {
        "success": True,
        "message": "Reindexing scheduled",
        "data": None,
        "errors": None,
        "meta": {"request_id": correlation_id},
    }
