"""
Pydantic models for the SHL Assessment Recommender System.

This file defines all the data structures used throughout the application:
- Message models for chat conversations
- Assessment models for SHL catalog items
- Request/response models for API endpoints
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, HttpUrl


class Message(BaseModel):
    """Represents a single message in the conversation."""
    role: Literal["user", "assistant"] = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message")


class ChatRequest(BaseModel):
    """Request model for the /chat endpoint."""
    messages: List[Message] = Field(..., description="List of messages in the conversation")


class Assessment(BaseModel):
    """Represents an SHL assessment from the catalog."""
    name: str = Field(..., description="Name of the assessment")
    url: str = Field(..., description="URL to the assessment page")
    test_type: str = Field(..., description="Type of test (e.g., 'Technical', 'Personality')")


class ChatResponse(BaseModel):
    """Response model for the /chat endpoint."""
    reply: str = Field(..., description="The assistant's reply")
    recommendations: List[Assessment] = Field(..., description="List of recommended assessments")
    end_of_conversation: bool = Field(False, description="Whether the conversation should end")


class HealthResponse(BaseModel):
    """Response model for the /health endpoint."""
    status: str = Field("ok", description="Health status of the service")


class CatalogItem(BaseModel):
    """Internal model for catalog items loaded from JSON."""
    name: str
    url: str
    description: str
    test_type: str
    duration: Optional[str] = None
    remote_testing: Optional[bool] = None
    
    def to_assessment(self) -> Assessment:
        """Convert to Assessment model for API responses."""
        return Assessment(
            name=self.name,
            url=self.url,
            test_type=self.test_type
        )
