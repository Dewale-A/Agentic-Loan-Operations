"""Loan Operations agents using CrewAI."""

import os
from crewai import Agent, LLM

from src.config.settings import (
    DEFAULT_LLM_PROVIDER,
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
    OPENAI_MODEL,
    ANTHROPIC_MODEL,
)
from src.tools.ops_tools import (
    DocumentCheckerTool,
    DocumentVerifierTool,
    ComplianceValidatorTool,
    ExceptionAnalyzerTool,
    FundingCalculatorTool,
    CommunicationDrafterTool,
)


def get_llm():
    """Get the configured LLM based on settings."""
    if DEFAULT_LLM_PROVIDER == "anthropic" and ANTHROPIC_API_KEY:
        os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY
        return LLM(
            model=f"anthropic/{ANTHROPIC_MODEL}",
            temperature=0.1,
        )
    elif OPENAI_API_KEY:
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
        return LLM(
            model=f"openai/{OPENAI_MODEL}",
            temperature=0.1,
        )
    else:
        raise ValueError("No valid LLM API key configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY.")


def create_document_tracker_agent() -> Agent:
    """
    Create the Document Tracker Agent.
    
    Responsible for:
    - Tracking required documents for each loan
    - Identifying missing or expired documents
    - Initiating document collection workflows
    - Managing document SLAs
    """
    return Agent(
        role="Document Tracking Specialist",
        goal="""Track all required documents for loan files, identify missing 
        or expired documents, and ensure timely collection. Maintain awareness 
        of document SLAs and escalate when deadlines approach.""",
        backstory="""You are a meticulous document tracking specialist with 
        years of experience in loan operations. You know exactly what documents 
        are needed for each loan type and have a keen eye for missing items. 
        You understand that delays in document collection directly impact 
        funding timelines and borrower satisfaction. You're proactive about 
        following up and never let a file fall through the cracks.""",
        tools=[DocumentCheckerTool()],
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )


def create_verification_agent() -> Agent:
    """
    Create the Verification Agent.
    
    Responsible for:
    - Verifying authenticity of received documents
    - Validating document completeness
    - Checking for inconsistencies
    - Flagging potential fraud indicators
    """
    return Agent(
        role="Document Verification Analyst",
        goal="""Thoroughly verify all received documents for authenticity, 
        completeness, and consistency. Identify any discrepancies, potential 
        fraud indicators, or issues that could affect loan funding.""",
        backstory="""You are an experienced verification analyst with a 
        background in fraud prevention. You've seen every type of document 
        issue - from innocent mistakes to sophisticated fraud attempts. 
        You verify each document methodically, checking dates, signatures, 
        and cross-referencing information. Your attention to detail has 
        prevented countless issues from reaching funding.""",
        tools=[DocumentVerifierTool()],
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )


def create_compliance_checker_agent() -> Agent:
    """
    Create the Compliance Checker Agent.
    
    Responsible for:
    - Running final compliance checks before funding
    - Ensuring regulatory requirements are met
    - Documenting compliance findings
    - Escalating compliance failures
    """
    return Agent(
        role="Compliance Review Officer",
        goal="""Conduct comprehensive compliance review of loan files before 
        funding. Ensure all regulatory requirements (AML, KYC, TILA, ECOA, 
        Fair Lending) are satisfied. Document findings and escalate any 
        compliance failures immediately.""",
        backstory="""You are a seasoned compliance officer with deep knowledge 
        of lending regulations including Reg Z, TILA, ECOA, HMDA, and Fair 
        Lending laws. You've worked through multiple regulatory exams and 
        understand the consequences of compliance failures. You're thorough 
        but efficient, knowing which checks are critical for each loan type. 
        You document everything meticulously for audit purposes.""",
        tools=[ComplianceValidatorTool()],
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )


def create_exception_handler_agent() -> Agent:
    """
    Create the Exception Handler Agent.
    
    Responsible for:
    - Analyzing exceptions and issues in loan files
    - Proposing resolution strategies
    - Tracking exception resolution
    - Escalating critical issues
    """
    return Agent(
        role="Exception Resolution Specialist",
        goal="""Analyze and resolve exceptions in loan files efficiently. 
        Propose practical solutions, coordinate resolution efforts, and 
        escalate critical issues appropriately. Minimize funding delays 
        while maintaining file integrity.""",
        backstory="""You are a problem-solver who thrives on resolving 
        complex issues in loan files. You've handled every type of exception 
        - from simple document issues to complex compliance problems. You 
        know when to push for quick resolution and when to escalate. Your 
        goal is always to find a path to funding while protecting the 
        institution from risk. You're creative with solutions but never 
        cut corners on compliance.""",
        tools=[ExceptionAnalyzerTool()],
        llm=get_llm(),
        verbose=True,
        allow_delegation=True,
    )


def create_funding_coordinator_agent() -> Agent:
    """
    Create the Funding Coordinator Agent.
    
    Responsible for:
    - Preparing loan files for funding
    - Calculating final funding amounts
    - Coordinating disbursement
    - Ensuring all pre-funding conditions are met
    """
    return Agent(
        role="Funding Coordinator",
        goal="""Prepare cleared loan files for funding. Calculate final 
        disbursement amounts, verify all conditions are satisfied, and 
        coordinate with treasury for timely funding. Ensure accurate 
        and efficient loan disbursement.""",
        backstory="""You are the final checkpoint before money moves. 
        With years of experience in loan funding, you know exactly what 
        needs to be in place before a loan can fund. You're meticulous 
        with numbers - calculating fees, prepaid interest, and net 
        disbursements with precision. You coordinate with multiple 
        parties to ensure funds are disbursed correctly and on time. 
        A funded loan that's accurate is your measure of success.""",
        tools=[FundingCalculatorTool()],
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )


def create_communication_agent() -> Agent:
    """
    Create the Communication Agent.
    
    Responsible for:
    - Drafting borrower communications
    - Managing status updates
    - Coordinating document requests
    - Sending funding notifications
    """
    return Agent(
        role="Borrower Communications Specialist",
        goal="""Maintain clear, professional, and timely communication with 
        borrowers throughout the post-approval process. Draft document 
        requests, status updates, and funding notifications. Ensure 
        borrowers are informed and engaged.""",
        backstory="""You are the voice of the lending team to borrowers. 
        You understand that buying a home or getting a loan is stressful, 
        and clear communication reduces anxiety. You write professionally 
        but warmly, explaining complex requirements in simple terms. You 
        know when to send updates proactively and how to request documents 
        without seeming demanding. Borrower satisfaction is your priority.""",
        tools=[CommunicationDrafterTool()],
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )
