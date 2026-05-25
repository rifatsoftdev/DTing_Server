from enum import Enum as PyEnum


class TransactionType(str, PyEnum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    SENDMONEY = "sendmoney"
    DEVPAY = "devpay"
    BILLPAY = "billpay"
    RECHARGE = "recharge"
    DONATION = "donation"
    REWARD = "reward"
    CASHBACK = "cashback"


class TransactionStatus(str, PyEnum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class TransactionDirection(str, PyEnum):
    IN = "in"
    OUT = "out"


class PaymentMethods(str, PyEnum):
    WALLET = "wallet"
    BKASH = "bkash"
    NAGAD = "nagad"
    UPAI = "upai"
    ROCKET = "rocket"
    BANK = "bank"


class BillCategory(str, PyEnum):
    INTERNET = "internet"
    ELECTRICITY = "electricity"
    WATER = "water"
    GAS = "gas"
    ECOMMERCE = "ecommerce"
    RENT = "rent"
    FOOD = "food"
    TRAVEL = "travel"
    MERCHANT = "merchant"
    TV = "tv"
    TELEPHONE = "telephone"
    OTHER = "other"