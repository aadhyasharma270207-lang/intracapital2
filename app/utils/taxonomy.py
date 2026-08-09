from enum import Enum


class AssetType(str, Enum):
    PATENT = "PATENT"
    RESEARCH = "RESEARCH"
    CUSTOMER_FEEDBACK = "CUSTOMER_FEEDBACK"
    CUSTOMER_DATA = "CUSTOMER_DATA"
    SENSOR_DATA = "SENSOR_DATA"
    API = "API"
    PRODUCT = "PRODUCT"
    TECHNOLOGY = "TECHNOLOGY"
    MANUFACTURING_PROCESS = "MANUFACTURING_PROCESS"
    MANUFACTURING_LOG = "MANUFACTURING_LOG"
    BUSINESS_DOCUMENT = "BUSINESS_DOCUMENT"
    EMPLOYEE_EXPERTISE = "EMPLOYEE_EXPERTISE"
    HISTORICAL_PROJECT = "HISTORICAL_PROJECT"
    OTHER = "OTHER"

    @classmethod
    def from_string(cls, value: str) -> "AssetType":
        if not value:
            return cls.OTHER
        normalized = value.strip().upper().replace(" ", "_")
        try:
            return cls[normalized]
        except KeyError:
            return cls.OTHER
