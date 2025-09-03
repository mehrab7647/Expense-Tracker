"""Enums for the expense tracker application."""

from enum import Enum


class TransactionType(Enum):
    """Enum for transaction types."""
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class CategoryType(Enum):
    """Enum for category types."""
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"