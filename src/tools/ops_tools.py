"""Tools for Loan Operations agents."""

import json
from datetime import datetime, timedelta
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from src.config.settings import REQUIRED_DOCUMENTS, COMPLIANCE_CHECKS, SLA_THRESHOLDS


class DocumentCheckerInput(BaseModel):
    """Input schema for document checker tool."""
    loan_id: str = Field(..., description="Loan ID to check documents for")
    loan_type: str = Field(..., description="Type of loan (mortgage, personal, auto, business)")
    documents_received: str = Field(..., description="JSON string of documents received with status")


class DocumentCheckerTool(BaseTool):
    """Check what documents are missing or need attention."""
    
    name: str = "document_checker"
    description: str = """Check required documents against received documents.
    
    Args:
        loan_id: The loan identifier
        loan_type: Type of loan (mortgage, personal, auto, business)
        documents_received: JSON string with document statuses
        
    Returns: JSON with missing documents, expired documents, and action items"""
    args_schema: Type[BaseModel] = DocumentCheckerInput
    
    def _run(self, loan_id: str, loan_type: str, documents_received: str) -> str:
        """Check documents and identify gaps."""
        required = REQUIRED_DOCUMENTS.get(loan_type, REQUIRED_DOCUMENTS["personal"])
        received = json.loads(documents_received) if documents_received else {}
        
        missing = []
        expired = []
        pending_verification = []
        
        for doc in required:
            if doc not in received:
                missing.append(doc)
            elif received[doc].get("status") == "pending":
                missing.append(doc)
            elif received[doc].get("status") == "expired":
                expired.append(doc)
            elif received[doc].get("status") == "received":
                pending_verification.append(doc)
        
        result = {
            "loan_id": loan_id,
            "loan_type": loan_type,
            "total_required": len(required),
            "missing_documents": missing,
            "expired_documents": expired,
            "pending_verification": pending_verification,
            "collection_complete": len(missing) == 0 and len(expired) == 0,
            "sla_hours_remaining": SLA_THRESHOLDS["document_follow_up"],
            "action_required": len(missing) > 0 or len(expired) > 0,
        }
        
        return json.dumps(result, indent=2)


class DocumentVerifierInput(BaseModel):
    """Input schema for document verifier tool."""
    document_name: str = Field(..., description="Name of document to verify")
    document_data: str = Field(..., description="JSON string with document details to verify")


class DocumentVerifierTool(BaseTool):
    """Verify a specific document's authenticity and completeness."""
    
    name: str = "document_verifier"
    description: str = """Verify a document's authenticity, completeness, and validity.
    
    Args:
        document_name: Name of the document
        document_data: JSON with document details (received_date, content summary, etc.)
        
    Returns: Verification result with pass/fail and findings"""
    args_schema: Type[BaseModel] = DocumentVerifierInput
    
    def _run(self, document_name: str, document_data: str) -> str:
        """Verify document."""
        data = json.loads(document_data) if document_data else {}
        
        # Simulated verification checks
        checks = {
            "document_present": True,
            "legible": True,
            "complete": data.get("pages_complete", True),
            "not_expired": True,
            "signatures_valid": data.get("signed", True),
            "dates_consistent": True,
        }
        
        # Check expiration for date-sensitive docs
        if document_name in ["proof_of_income", "bank_statements"]:
            doc_date = data.get("document_date")
            if doc_date:
                doc_datetime = datetime.strptime(doc_date, "%Y-%m-%d")
                if (datetime.now() - doc_datetime).days > 90:
                    checks["not_expired"] = False
        
        all_passed = all(checks.values())
        failed_checks = [k for k, v in checks.items() if not v]
        
        result = {
            "document_name": document_name,
            "verification_passed": all_passed,
            "verification_date": datetime.now().isoformat(),
            "checks_performed": checks,
            "failed_checks": failed_checks,
            "recommendation": "VERIFIED" if all_passed else "REQUIRES_ATTENTION",
            "notes": f"Document {'verified successfully' if all_passed else 'failed verification: ' + ', '.join(failed_checks)}",
        }
        
        return json.dumps(result, indent=2)


class ComplianceValidatorInput(BaseModel):
    """Input schema for compliance validator tool."""
    loan_id: str = Field(..., description="Loan ID to validate")
    loan_data: str = Field(..., description="JSON string with loan details")


class ComplianceValidatorTool(BaseTool):
    """Validate loan against compliance requirements."""
    
    name: str = "compliance_validator"
    description: str = """Run compliance checks on a loan file.
    
    Args:
        loan_id: The loan identifier
        loan_data: JSON with loan details (amount, rate, borrower info, etc.)
        
    Returns: Compliance check results with pass/fail for each requirement"""
    args_schema: Type[BaseModel] = ComplianceValidatorInput
    
    def _run(self, loan_id: str, loan_data: str) -> str:
        """Run compliance validation."""
        data = json.loads(loan_data) if loan_data else {}
        
        results = {}
        for check in COMPLIANCE_CHECKS:
            # Simulated compliance checks
            if check == "anti_money_laundering":
                passed = data.get("aml_cleared", True)
                findings = None if passed else "AML flag detected - requires review"
            elif check == "know_your_customer":
                passed = data.get("kyc_verified", True)
                findings = None if passed else "KYC verification incomplete"
            elif check == "truth_in_lending":
                passed = data.get("tila_disclosed", True)
                findings = None if passed else "TILA disclosure missing"
            elif check == "equal_credit_opportunity":
                passed = True  # Assume passed unless flagged
                findings = None
            elif check == "fair_lending":
                passed = True
                findings = None
            elif check == "flood_insurance":
                # Required for properties in flood zones
                if data.get("loan_type") == "mortgage":
                    passed = data.get("flood_cert_clear", True) or data.get("flood_insurance_obtained", False)
                    findings = None if passed else "Flood insurance required but not obtained"
                else:
                    passed = True
                    findings = "N/A - not a mortgage"
            else:
                passed = True
                findings = None
            
            results[check] = {
                "check_name": check,
                "passed": passed,
                "findings": findings,
                "checked_date": datetime.now().isoformat(),
            }
        
        all_passed = all(r["passed"] for r in results.values())
        failed = [k for k, v in results.items() if not v["passed"]]
        
        return json.dumps({
            "loan_id": loan_id,
            "compliance_passed": all_passed,
            "total_checks": len(COMPLIANCE_CHECKS),
            "passed_checks": len(COMPLIANCE_CHECKS) - len(failed),
            "failed_checks": failed,
            "results": results,
            "recommendation": "CLEARED" if all_passed else "REQUIRES_REMEDIATION",
        }, indent=2)


class ExceptionAnalyzerInput(BaseModel):
    """Input schema for exception analyzer tool."""
    exception_type: str = Field(..., description="Type of exception (document, compliance, verification, funding)")
    exception_details: str = Field(..., description="JSON string with exception details")


class ExceptionAnalyzerTool(BaseTool):
    """Analyze exceptions and propose resolutions."""
    
    name: str = "exception_analyzer"
    description: str = """Analyze an exception and propose resolution options.
    
    Args:
        exception_type: Category of exception (document, compliance, verification, funding)
        exception_details: JSON with specific exception details
        
    Returns: Analysis with severity, impact, and proposed resolution steps"""
    args_schema: Type[BaseModel] = ExceptionAnalyzerInput
    
    def _run(self, exception_type: str, exception_details: str) -> str:
        """Analyze exception and propose solutions."""
        details = json.loads(exception_details) if exception_details else {}
        
        # Resolution strategies by exception type
        resolutions = {
            "document": {
                "missing": ["Request document from borrower", "Set follow-up reminder", "Escalate if SLA breached"],
                "expired": ["Request updated document", "Verify if recent version exists"],
                "illegible": ["Request clearer copy", "Accept if key information readable"],
                "incomplete": ["Request missing pages", "Verify completeness requirements"],
            },
            "compliance": {
                "failed_check": ["Review findings", "Request remediation", "Escalate to compliance officer"],
                "pending_review": ["Expedite review", "Provide additional documentation"],
                "requires_override": ["Document justification", "Obtain management approval"],
            },
            "verification": {
                "mismatch": ["Investigate discrepancy", "Request clarification from borrower"],
                "unable_to_verify": ["Try alternate verification method", "Request additional proof"],
                "fraud_flag": ["Escalate immediately", "Suspend processing", "Notify fraud team"],
            },
            "funding": {
                "insufficient_funds": ["Verify funding source", "Delay funding date"],
                "wire_error": ["Verify wire instructions", "Resubmit wire request"],
                "hold_required": ["Identify hold reason", "Resolve blocking issues"],
            },
        }
        
        issue = details.get("issue", "unknown")
        available_resolutions = resolutions.get(exception_type, {}).get(issue, ["Escalate to supervisor"])
        
        # Determine severity
        severity = "medium"
        if exception_type == "verification" and issue == "fraud_flag":
            severity = "critical"
        elif exception_type == "compliance" and issue == "failed_check":
            severity = "high"
        elif exception_type == "document" and issue == "missing":
            severity = "low"
        
        result = {
            "exception_type": exception_type,
            "issue": issue,
            "severity": severity,
            "impact_assessment": f"{'Blocks funding' if severity in ['high', 'critical'] else 'May delay funding'}",
            "proposed_resolutions": available_resolutions,
            "recommended_action": available_resolutions[0] if available_resolutions else "Escalate",
            "escalation_required": severity in ["high", "critical"],
            "sla_impact": severity != "low",
        }
        
        return json.dumps(result, indent=2)


class FundingCalculatorInput(BaseModel):
    """Input schema for funding calculator tool."""
    loan_amount: float = Field(..., description="Approved loan amount")
    interest_rate: float = Field(..., description="Annual interest rate as percentage")
    loan_type: str = Field(..., description="Type of loan")
    fees: str = Field(default="{}", description="JSON string of applicable fees")


class FundingCalculatorTool(BaseTool):
    """Calculate funding amounts and prepare disbursement details."""
    
    name: str = "funding_calculator"
    description: str = """Calculate final funding amounts and disbursement breakdown.
    
    Args:
        loan_amount: The approved loan amount
        interest_rate: Annual interest rate (e.g., 6.5 for 6.5%)
        loan_type: Type of loan (mortgage, personal, auto, business)
        fees: JSON with applicable fees
        
    Returns: Funding breakdown with net disbursement amount"""
    args_schema: Type[BaseModel] = FundingCalculatorInput
    
    def _run(self, loan_amount: float, interest_rate: float, loan_type: str, fees: str = "{}") -> str:
        """Calculate funding details."""
        fee_data = json.loads(fees) if fees else {}
        
        # Standard fees by loan type
        standard_fees = {
            "mortgage": {
                "origination_fee": loan_amount * 0.01,
                "appraisal_fee": 500,
                "title_insurance": 1200,
                "recording_fee": 150,
            },
            "personal": {
                "origination_fee": loan_amount * 0.02,
                "processing_fee": 100,
            },
            "auto": {
                "origination_fee": loan_amount * 0.015,
                "documentation_fee": 75,
            },
            "business": {
                "origination_fee": loan_amount * 0.02,
                "documentation_fee": 500,
                "ucc_filing_fee": 200,
            },
        }
        
        applicable_fees = standard_fees.get(loan_type, standard_fees["personal"])
        applicable_fees.update(fee_data)
        
        total_fees = sum(applicable_fees.values())
        net_disbursement = loan_amount - total_fees
        
        # Prepaid interest (assuming funding mid-month)
        daily_interest = (loan_amount * (interest_rate / 100)) / 365
        prepaid_days = 15  # Assume 15 days to end of month
        prepaid_interest = daily_interest * prepaid_days
        
        result = {
            "loan_amount": loan_amount,
            "interest_rate": interest_rate,
            "loan_type": loan_type,
            "fee_breakdown": applicable_fees,
            "total_fees": round(total_fees, 2),
            "prepaid_interest": round(prepaid_interest, 2),
            "net_disbursement": round(net_disbursement - prepaid_interest, 2),
            "funding_method": "wire" if loan_amount > 50000 else "ach",
            "estimated_funding_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        }
        
        return json.dumps(result, indent=2)


class CommunicationDrafterInput(BaseModel):
    """Input schema for communication drafter tool."""
    communication_type: str = Field(..., description="Type: document_request, status_update, funding_notice, exception_notice")
    recipient_name: str = Field(..., description="Borrower's name")
    context: str = Field(..., description="JSON string with relevant context for the communication")


class CommunicationDrafterTool(BaseTool):
    """Draft borrower communications."""
    
    name: str = "communication_drafter"
    description: str = """Draft professional borrower communications.
    
    Args:
        communication_type: Type of communication (document_request, status_update, funding_notice, exception_notice)
        recipient_name: Borrower's name
        context: JSON with relevant details for the communication
        
    Returns: Drafted communication ready for review and sending"""
    args_schema: Type[BaseModel] = CommunicationDrafterInput
    
    def _run(self, communication_type: str, recipient_name: str, context: str) -> str:
        """Draft communication."""
        ctx = json.loads(context) if context else {}
        
        templates = {
            "document_request": f"""
Dear {recipient_name},

We are processing your loan application and need the following document(s) to proceed:

{chr(10).join('• ' + doc for doc in ctx.get('missing_documents', ['Required document']))}

Please submit these documents at your earliest convenience. You can:
- Upload securely through our portal
- Email to loans@example.com
- Fax to (555) 123-4567

If you have any questions, please contact us at (555) 987-6543.

Thank you for your prompt attention to this matter.

Best regards,
Loan Operations Team
""",
            "status_update": f"""
Dear {recipient_name},

This is an update on your loan application (Loan #{ctx.get('loan_id', 'N/A')}):

Current Status: {ctx.get('status', 'In Progress')}
{f"Next Steps: {ctx.get('next_steps', '')}" if ctx.get('next_steps') else ''}
{f"Estimated Funding Date: {ctx.get('funding_date', '')}" if ctx.get('funding_date') else ''}

We will keep you informed of any updates. If you have questions, please don't hesitate to reach out.

Best regards,
Loan Operations Team
""",
            "funding_notice": f"""
Dear {recipient_name},

Great news! Your loan (#{ctx.get('loan_id', 'N/A')}) has been approved for funding.

Funding Details:
- Loan Amount: ${ctx.get('loan_amount', 0):,.2f}
- Net Disbursement: ${ctx.get('net_disbursement', 0):,.2f}
- Funding Method: {ctx.get('funding_method', 'Wire Transfer')}
- Expected Funding Date: {ctx.get('funding_date', 'Within 2 business days')}

Please ensure your receiving account information is accurate. Funds will be disbursed to:
Account ending in: {ctx.get('account_last4', '****')}

Congratulations on your new loan!

Best regards,
Loan Operations Team
""",
            "exception_notice": f"""
Dear {recipient_name},

We've encountered an issue while processing your loan application that requires your attention:

Issue: {ctx.get('issue_description', 'Additional information needed')}

Action Required: {ctx.get('action_required', 'Please contact us')}

This may affect your expected funding timeline. Please respond within {ctx.get('response_deadline', '48 hours')} to avoid delays.

Contact us at (555) 987-6543 or reply to this message.

Thank you for your cooperation.

Best regards,
Loan Operations Team
""",
        }
        
        draft = templates.get(communication_type, templates["status_update"])
        
        result = {
            "communication_type": communication_type,
            "recipient": recipient_name,
            "subject": {
                "document_request": f"Action Required: Documents Needed for Loan #{ctx.get('loan_id', '')}",
                "status_update": f"Loan Status Update - #{ctx.get('loan_id', '')}",
                "funding_notice": f"Congratulations! Your Loan is Ready for Funding",
                "exception_notice": f"Action Required: Issue with Your Loan Application",
            }.get(communication_type, "Loan Update"),
            "body": draft.strip(),
            "priority": "high" if communication_type in ["document_request", "exception_notice"] else "normal",
            "drafted_at": datetime.now().isoformat(),
        }
        
        return json.dumps(result, indent=2)
