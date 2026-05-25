import phonenumbers
import re
from phonenumbers.phonenumberutil import NumberParseException


class Validator:
    # check if phone number is valid for given country
    @staticmethod
    def validate_phone(number: str, country_iso: str) -> bool:
        try:
            parsed = phonenumbers.parse(number, country_iso)
            return phonenumbers.is_valid_number(parsed)
        except NumberParseException:
            return False

    # basic email validation using regex
    @staticmethod
    def valid_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
