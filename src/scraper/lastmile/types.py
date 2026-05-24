from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CategoryName(BaseModel):
    lt: str = ""
    ru: str = ""
    en: str = ""


class LocalizedString(BaseModel):
    lt: str = ""
    ru: str = ""
    en: str = ""
    de: str = ""


class ProductNutrition(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, serialize_by_alias=True)

    energy: str
    fat: str
    sat_fat: str
    carbs: str
    sugar: str
    protein: str
    salt: str


class ProductPrice(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, serialize_by_alias=True)

    p: float | None
    s: float | None
    l: float | None  # noqa: E741
    still: float | None
    ltill: str | None
    ap: float | None
    lap: float | None
    lstill: float | None


class ProductDimensions(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, serialize_by_alias=True)

    length: float
    width: float
    height: float


class LastMileCategoryPayload(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    name: CategoryName
    icon: str
    icon_url: str
    thumb_url: str
    rank: int
    parent_id: str
    store_ids: list[str]
    chain_id: str
    chain_ids: list[str]
    country_ids: list[str]
    picking_rank: int
    show: bool
    mapping: dict
    minimum_stock: int | None
    date_last_refresh: int
    slugs: list[str]
    metadata: dict
    seo_title: dict
    seo_description: dict
    category_description: dict
    subcategories: list
    global_category_id: str
    global_category_parent_id: str


class LastMileCategoriesResponse(BaseModel):
    data: list[LastMileCategoryPayload]
    count: int


class LastMileProductPayload(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    internal_id: str = Field("", alias="_id")
    category_id: str
    chain_id: str
    constraint_code: str
    conversion_measure: str
    conversion_to_kg: float
    conversion_value: float
    country_of_origin: str
    date_created: str
    deposit_price: float
    dimensions: ProductDimensions
    erp_code: str
    has_nutritions: bool
    is_active: bool
    is_approved: bool
    is_fixed_weight: bool
    is_in_stock: bool
    is_promo: bool
    last_month_lowest_price: float
    maximum_order_quantity: int
    name: LocalizedString
    description: LocalizedString
    allergens: LocalizedString
    storing_conditions: LocalizedString
    ingredients: LocalizedString
    manufacturer_contact: LocalizedString
    safety_information: LocalizedString
    product_label: LocalizedString
    nutrition: ProductNutrition
    actual_price: float
    photo_url: str
    thumb_url: str
    product_id: str
    prc: ProductPrice
    cost_price: ProductPrice
    promo: dict | None
    promo_tags: dict
    slugs: list[str]
    standard_order_quantity: int
    store_ids: list[str]
    supplier: str
    tags: list
    unit_of_measure: str
    unit_weight: float


class LastMileProductEntry(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    front_end_product: LastMileProductPayload
    position: int
    karma_adjustment: int


class LastMileProductsResponse(BaseModel):
    status: str
    products: list[LastMileProductEntry]
    count: int
