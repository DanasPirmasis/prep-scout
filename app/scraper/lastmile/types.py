from typing import TypedDict


class CategoryName(TypedDict):
    lt: str
    ru: str
    en: str


class LastMileCategory(TypedDict):
    id: str
    name: CategoryName
    icon: str
    iconUrl: str
    thumbUrl: str
    rank: int
    parentId: str
    storeIds: list[str]
    chainId: str
    chainIds: list[str]
    countryIds: list[str]
    pickingRank: int
    show: bool
    mapping: dict
    minimumStock: int | None
    dateLastRefresh: int  # millisecond timestamp, stored as str to avoid integer overflow
    slugs: list[str]
    metadata: dict
    seoTitle: dict
    seoDescription: dict
    categoryDescription: dict
    subcategories: list
    globalCategoryId: str
    globalCategoryParentId: str


class LastMileCategoriesResponse(TypedDict):
    data: list[LastMileCategory]
    count: int


class LocalizedString(TypedDict, total=False):
    lt: str
    ru: str
    en: str
    de: str


class ProductNutrition(TypedDict):
    energy: str
    fat: str
    satFat: str
    carbs: str
    sugar: str
    protein: str
    salt: str


class ProductPrice(TypedDict):
    p: float | None
    s: float | None
    l: float | None
    still: float | None
    ltill: str | None
    ap: float | None
    lap: float | None
    lstill: float | None


class ProductDimensions(TypedDict):
    length: float
    width: float
    height: float


class LastMileProduct(TypedDict):
    id: str
    _id: str
    categoryId: str
    chainId: str
    constraintCode: str
    conversionMeasure: str
    conversionToKg: float
    conversionValue: float
    countryOfOrigin: str
    dateCreated: str
    depositPrice: float
    dimensions: ProductDimensions
    erpCode: str
    hasNutritions: bool
    isActive: bool
    isApproved: bool
    isFixedWeight: bool
    isInStock: bool
    isPromo: bool
    lastMonthLowestPrice: float
    maximumOrderQuantity: int
    name: LocalizedString
    description: LocalizedString
    allergens: LocalizedString
    storingConditions: LocalizedString
    ingredients: LocalizedString
    manufacturerContact: LocalizedString
    safetyInformation: LocalizedString
    productLabel: LocalizedString
    nutrition: ProductNutrition
    actualPrice: float
    photoUrl: str
    thumbUrl: str
    productId: str
    prc: ProductPrice
    costPrice: ProductPrice
    promo: dict | None
    promoTags: dict
    slugs: list[str]
    standardOrderQuantity: int
    storeIds: list[str]
    supplier: str
    tags: list
    unitOfMeasure: str
    unitWeight: float


class LastMileProductEntry(TypedDict):
    frontEndProduct: LastMileProduct
    position: int
    karmaAdjustment: int


class LastMileProductsResponse(TypedDict):
    status: str
    products: list[LastMileProductEntry]
    count: int
