"""Loan file models for post-approval operations."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
import json


class DocumentStatus(Enum):
    """Status of a required document."""
    PENDING = "pending"
    RECEIVED = "received"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class FundingStatus(Enum):
    """Overall funding pipeline status."""
    APPROVED = "approved"                    # Just approved, entering operations
    DOCUMENT_COLLECTION = "document_collection"  # Collecting required docs
    VERIFICATION = "verification"            # Verifying documents
    COMPLIANCE_REVIEW = "compliance_review"  # Final compliance check
    EXCEPTION_HANDLING = "exception_handling"  # Handling issues
    READY_TO_FUND = "ready_to_fund"         # All clear, prepare funding
    FUNDED = "funded"                        # Loan funded
    SUSPENDED = "suspended"                  # On hold due to issues


@dataclass
class Document:
    """Individual document in loan file."""
    name: str
    status: DocumentStatus = DocumentStatus.PENDING
    received_date: Optional[str] = None
    verified_date: Optional[str] = None
    verified_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    expiration_date: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class ComplianceCheck:
    """Individual compliance check result."""
    check_name: str
    passed: Optional[bool] = None
    checked_date: Optional[str] = None
    checked_by: Optional[str] = None
    findings: Optional[str] = None
    requires_override: bool = False


@dataclass
class Exception:
    """Exception/issue in the loan file."""
    exception_id: str
    category: str
    description: str
    severity: str  # low, medium, high, critical
    created_date: str
    resolved_date: Optional[str] = None
    resolution: Optional[str] = None
    assigned_to: Optional[str] = None


@dataclass
class LoanFile:
    """Complete loan file for post-approval operations."""
    # Core identifiers
    loan_id: str
    borrower_name: str
    borrower_email: str
    borrower_phone: str
    
    # Loan details
    loan_type: str  # mortgage, personal, auto, business
    loan_amount: float
    interest_rate: float
    term_months: int
    
    # Approval info
    approval_date: str
    approval_conditions: List[str] = field(default_factory=list)
    underwriter: str = ""
    
    # Operations status
    funding_status: FundingStatus = FundingStatus.APPROVED
    target_funding_date: Optional[str] = None
    actual_funding_date: Optional[str] = None
    
    # Documents
    documents: Dict[str, Document] = field(default_factory=dict)
    
    # Compliance
    compliance_checks: Dict[str, ComplianceCheck] = field(default_factory=dict)
    
    # Exceptions
    exceptions: List[Exception] = field(default_factory=list)
    
    # Communication log
    communications: List[Dict] = field(default_factory=list)
    
    # Funding details
    funding_amount: Optional[float] = None
    funding_method: Optional[str] = None  # wire, ach, check
    disbursement_account: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "loan_id": self.loan_id,
            "borrower_name": self.borrower_name,
            "borrower_email": self.borrower_email,
            "borrower_phone": self.borrower_phone,
            "loan_type": self.loan_type,
            "loan_amount": self.loan_amount,
            "interest_rate": self.interest_rate,
            "term_months": self.term_months,
            "approval_date": self.approval_date,
            "approval_conditions": self.approval_conditions,
            "underwriter": self.underwriter,
            "funding_status": self.funding_status.value,
            "target_funding_date": self.target_funding_date,
            "actual_funding_date": self.actual_funding_date,
            "documents": {k: {"name": v.name, "status": v.status.value, 
                            "received_date": v.received_date, "verified_date": v.verified_date}
                        for k, v in self.documents.items()},
            "compliance_checks": {k: {"check_name": v.check_name, "passed": v.passed,
                                     "findings": v.findings}
                                 for k, v in self.compliance_checks.items()},
            "exceptions": [{"id": e.exception_id, "category": e.category,
                          "description": e.description, "severity": e.severity,
                          "resolved": e.resolved_date is not None}
                         for e in self.exceptions],
            "communications": self.communications,
        }
    
    @classmethod
    def from_json(cls, json_path: str) -> "LoanFile":
        """Load loan file from JSON."""
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Parse documents
        documents = {}
        for doc_name, doc_data in data.get("documents", {}).items():
            documents[doc_name] = Document(
                name=doc_data.get("name", doc_name),
                status=DocumentStatus(doc_data.get("status", "pending")),
                received_date=doc_data.get("received_date"),
                verified_date=doc_data.get("verified_date"),
            )
        
        # Parse compliance checks
        compliance_checks = {}
        for check_name, check_data in data.get("compliance_checks", {}).items():
            compliance_checks[check_name] = ComplianceCheck(
                check_name=check_data.get("check_name", check_name),
                passed=check_data.get("passed"),
                findings=check_data.get("findings"),
            )
        
        # Parse exceptions
        exceptions = []
        for exc_data in data.get("exceptions", []):
            exceptions.append(Exception(
                exception_id=exc_data.get("id", ""),
                category=exc_data.get("category", ""),
                description=exc_data.get("description", ""),
                severity=exc_data.get("severity", "medium"),
                created_date=exc_data.get("created_date", ""),
                resolved_date=exc_data.get("resolved_date"),
                resolution=exc_data.get("resolution"),
            ))
        
        return cls(
            loan_id=data["loan_id"],
            borrower_name=data["borrower_name"],
            borrower_email=data["borrower_email"],
            borrower_phone=data.get("borrower_phone", ""),
            loan_type=data["loan_type"],
            loan_amount=data["loan_amount"],
            interest_rate=data["interest_rate"],
            term_months=data["term_months"],
            approval_date=data["approval_date"],
            approval_conditions=data.get("approval_conditions", []),
            underwriter=data.get("underwriter", ""),
            funding_status=FundingStatus(data.get("funding_status", "approved")),
            target_funding_date=data.get("target_funding_date"),
            documents=documents,
            compliance_checks=compliance_checks,
            exceptions=exceptions,
            communications=data.get("communications", []),
        )
