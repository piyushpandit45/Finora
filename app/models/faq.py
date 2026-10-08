from uuid import UUID, uuid4
from beanie import Document
from pydantic import Field
from pydantic.config import ConfigDict


class FAQ(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    question: str = Field(...)
    answer: str = Field(...)
    category: str = Field(...)

    class Settings:
        name = "faqs"
        indexes = [
            "category",
        ]

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
