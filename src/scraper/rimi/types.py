from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RimiCategoriesResponse(BaseModel):
    model_config = ConfigDict(extra="allow")


class RimiProductsPageResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    totalPages: int
    products: list[Any] = Field(default_factory=list)
