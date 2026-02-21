"""Configuration settings for Loan Operations system."""

import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Model Settings
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "openai")

# Directory Settings
SAMPLE_LOANS_DIR = os.getenv("SAMPLE_LOANS_DIR", "./sample_loans")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")

# Document Requirements by Loan Type
REQUIRED_DOCUMENTS = {
    "mortgage": [
        "signed_application",
        "proof_of_income",
        "bank_statements",
        "tax_returns",
        "property_appraisal",
        "title_insurance",
        "homeowners_insurance",
        "flood_certification",
    ],
    "personal": [
        "signed_application",
        "proof_of_income",
        "bank_statements",
        "proof_of_identity",
    ],
    "auto": [
        "signed_application",
        "proof_of_income",
        "proof_of_insurance",
        "vehicle_title",
        "purchase_agreement",
    ],
    "business": [
        "signed_application",
        "business_tax_returns",
        "financial_statements",
        "business_license",
        "personal_guarantee",
        "collateral_documentation",
    ],
}

# Compliance Checks
COMPLIANCE_CHECKS = [
    "anti_money_laundering",
    "know_your_customer",
    "truth_in_lending",
    "equal_credit_opportunity",
    "fair_lending",
    "flood_insurance",
    "privacy_disclosure",
]

# SLA Thresholds (in hours)
SLA_THRESHOLDS = {
    "document_follow_up": 24,      # Chase borrower after 24 hours
    "verification_completion": 48,  # Complete verification within 48 hours
    "compliance_review": 24,        # Compliance review within 24 hours
    "funding_preparation": 24,      # Prepare funding within 24 hours
    "total_to_funding": 120,        # Total time to funding: 5 business days
}

# Exception Categories
EXCEPTION_CATEGORIES = {
    "document": ["missing", "expired", "illegible", "incomplete"],
    "compliance": ["failed_check", "pending_review", "requires_override"],
    "verification": ["mismatch", "unable_to_verify", "fraud_flag"],
    "funding": ["insufficient_funds", "wire_error", "hold_required"],
}
