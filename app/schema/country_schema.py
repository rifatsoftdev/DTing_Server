from pydantic import BaseModel, ConfigDict
from typing import Any, Dict, Optional




# Country Out
class CountryOut(BaseModel):
    country_id: str
    country_name: str
    country_code: str
    flag_emoji: str
    currency: str
    currency_symbol: str

    model_config = ConfigDict(from_attributes=True)


# new country request
class NewCountryRequest(BaseModel):
    user_id: str
    access_token: str
    device_id: str
    device_uuid: str

    country_id: str
    country_name: str
    country_code: str
    flag_emoji: str
    currency: str
    currency_symbol: str
    
    model_config = ConfigDict(from_attributes=True)


class DisableCountryRequest(BaseModel):
    user_id: str
    access_token: str
    device_id: Optional[str] = None
    device_uuid: Optional[str] = None
    android_id: Optional[str] = None
    android_uuid: Optional[str] = None
    user_password: str
    counrty_id: str
