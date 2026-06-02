from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RimiProductGtmEecProduct(BaseModel):
    id: str
    name: str
    category: str
    brand: str | None
    price: float
    currency: str


class RimiProductCard(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    product_code: str = Field(alias="data-product-code")
    gtm_eec_product: RimiProductGtmEecProduct = Field(alias="data-gtm-eec-product")
    url: str
    image_url: str | None = None
    name: str
    price_text: str | None = None
    unit_price_text: str | None = None
    comparative_unit: str | None = None


class RimiCategoriesResponse(BaseModel):
    model_config = ConfigDict(extra="allow")


class RimiProductsPageResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    totalPages: int
    products: list[Any] = Field(default_factory=list)
