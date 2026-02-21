"""Task definitions for Loan Operations crew."""

from crewai import Task, Agent


def create_document_tracking_task(agent: Agent, loan_context: str) -> Task:
    """
    Create the document tracking task.
    
    This task identifies missing documents and prepares the collection strategy.
    """
    return Task(
        description=f"""Review the loan file and identify all document requirements.

Loan Context:
{loan_context}

Your responsibilities:
1. Identify ALL required documents for this loan type
2. Check which documents have been received and their status
3. List any MISSING documents that must be collected
4. Identify any EXPIRED documents that need to be refreshed
5. Note any documents pending verification
6. Calculate time since last borrower contact
7. Recommend follow-up priority (urgent/normal/low)

Use the document_checker tool to analyze the loan file.

Output a clear document status report with:
- Complete list of required documents
- Status of each document (received/pending/missing/expired)
- Action items for document collection
- Recommended follow-up timeline
""",
        expected_output="""A comprehensive document tracking report containing:
1. Document inventory with status for each required document
2. List of missing documents with priority ranking
3. List of expired documents requiring refresh
4. Recommended actions and follow-up timeline
5. Risk assessment if documents are not received timely""",
        agent=agent,
    )


def create_verification_task(agent: Agent, loan_context: str) -> Task:
    """
    Create the document verification task.
    
    This task verifies received documents for authenticity and completeness.
    """
    return Task(
        description=f"""Verify all received documents in the loan file.

Loan Context:
{loan_context}

Your responsibilities:
1. Review each RECEIVED document for authenticity
2. Verify document completeness (all pages, signatures present)
3. Check document dates are current and valid
4. Cross-reference information across documents for consistency
5. Flag any discrepancies or potential fraud indicators
6. Document your verification findings

Use the document_verifier tool for each document requiring verification.

For each document, verify:
- Document is legible and complete
- Signatures are present where required
- Dates are within acceptable ranges
- Information matches application data
- No signs of alteration or fraud
""",
        expected_output="""A verification report containing:
1. Verification status for each document reviewed
2. List of documents that passed verification
3. List of documents with issues (and specific issues found)
4. Any fraud flags or concerns
5. Recommendation on whether file is ready for compliance review""",
        agent=agent,
    )


def create_compliance_review_task(agent: Agent, loan_context: str) -> Task:
    """
    Create the compliance review task.
    
    This task performs final compliance checks before funding.
    """
    return Task(
        description=f"""Conduct comprehensive compliance review of the loan file.

Loan Context:
{loan_context}

Your responsibilities:
1. Run ALL required compliance checks for this loan type
2. Verify Anti-Money Laundering (AML) clearance
3. Confirm Know Your Customer (KYC) requirements are met
4. Check Truth in Lending Act (TILA) disclosures
5. Verify Equal Credit Opportunity Act (ECOA) compliance
6. Confirm Fair Lending requirements
7. Check flood insurance requirements (if applicable)
8. Verify all required disclosures were provided

Use the compliance_validator tool to run the compliance checks.

Document any findings, especially:
- Any failed compliance checks
- Required remediations
- Checks requiring override approval
- Regulatory documentation requirements
""",
        expected_output="""A compliance review report containing:
1. Status of each compliance check (pass/fail/pending)
2. Detailed findings for any failed checks
3. Required remediation actions
4. Any items requiring management override
5. Final compliance recommendation (cleared/not cleared)
6. Documentation for audit trail""",
        agent=agent,
    )


def create_exception_handling_task(agent: Agent, loan_context: str) -> Task:
    """
    Create the exception handling task.
    
    This task analyzes and resolves any exceptions in the loan file.
    """
    return Task(
        description=f"""Analyze and propose resolutions for all exceptions in the loan file.

Loan Context:
{loan_context}

Your responsibilities:
1. Review all exceptions identified by other agents
2. Categorize exceptions by type (document/compliance/verification/funding)
3. Assess severity and funding impact of each exception
4. Propose specific resolution strategies
5. Identify which exceptions block funding vs. can be resolved post-funding
6. Recommend escalation path for critical issues
7. Create action plan with owners and timelines

Use the exception_analyzer tool to analyze each exception.

Consider:
- Can this be resolved quickly or does it require borrower action?
- Is there an alternative approach to satisfy the requirement?
- What is the risk of proceeding vs. waiting for resolution?
- Who needs to be involved in the resolution?
""",
        expected_output="""An exception analysis report containing:
1. List of all exceptions with severity ratings
2. Root cause analysis for each exception
3. Proposed resolution for each exception
4. Estimated resolution timeline
5. Escalation recommendations for critical issues
6. Impact assessment on funding timeline
7. Recommended path forward (proceed/hold/cancel)""",
        agent=agent,
    )


def create_funding_preparation_task(agent: Agent, loan_context: str) -> Task:
    """
    Create the funding preparation task.
    
    This task prepares cleared loans for disbursement.
    """
    return Task(
        description=f"""Prepare the loan for funding and calculate disbursement amounts.

Loan Context:
{loan_context}

Your responsibilities:
1. Confirm all pre-funding conditions are satisfied
2. Calculate final loan amount and applicable fees
3. Determine net disbursement amount
4. Calculate any prepaid interest
5. Verify disbursement account information
6. Determine appropriate funding method (wire/ACH/check)
7. Prepare funding package for treasury

Use the funding_calculator tool to calculate funding amounts.

Ensure accuracy in:
- Fee calculations (origination, closing costs, etc.)
- Prepaid interest calculation
- Net disbursement amount
- Funding instructions
""",
        expected_output="""A funding preparation package containing:
1. Confirmation that all conditions are satisfied
2. Complete fee breakdown
3. Final disbursement amount calculation
4. Prepaid interest calculation
5. Funding method and instructions
6. Disbursement account verification
7. Funding authorization request
8. Target funding date""",
        agent=agent,
    )


def create_communication_task(agent: Agent, loan_context: str, communication_needs: str) -> Task:
    """
    Create the borrower communication task.
    
    This task drafts and manages borrower communications.
    """
    return Task(
        description=f"""Draft appropriate borrower communications based on loan status.

Loan Context:
{loan_context}

Communication Needs:
{communication_needs}

Your responsibilities:
1. Review the current loan status and recent activity
2. Determine what communications are needed
3. Draft professional, clear communications
4. Ensure appropriate urgency is conveyed
5. Include all necessary details and instructions
6. Maintain warm but professional tone

Use the communication_drafter tool to create communications.

Communication types to consider:
- Document request (if documents are missing)
- Status update (routine progress update)
- Exception notice (if issues need borrower attention)
- Funding notice (when ready to fund)

Ensure communications:
- Are clear and easy to understand
- Include specific action items if needed
- Have appropriate deadlines
- Provide contact information for questions
""",
        expected_output="""Drafted communications including:
1. Appropriate communication type for current status
2. Professional email/letter body
3. Clear subject line
4. Any required attachments or forms referenced
5. Recommended send time/priority
6. Follow-up schedule if no response""",
        agent=agent,
    )
