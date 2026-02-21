"""Loan Operations Crew - Orchestrating post-approval loan processing."""

import json
from typing import Optional
from crewai import Crew, Process

from src.agents.ops_agents import (
    create_document_tracker_agent,
    create_verification_agent,
    create_compliance_checker_agent,
    create_exception_handler_agent,
    create_funding_coordinator_agent,
    create_communication_agent,
)
from src.tasks.ops_tasks import (
    create_document_tracking_task,
    create_verification_task,
    create_compliance_review_task,
    create_exception_handling_task,
    create_funding_preparation_task,
    create_communication_task,
)
from src.models.loan_file import LoanFile


class LoanOperationsCrew:
    """
    Orchestrates the post-approval loan operations workflow.
    
    This crew handles everything from approval to funding:
    1. Document Tracking - Identify missing documents
    2. Verification - Verify received documents
    3. Compliance Review - Final compliance checks
    4. Exception Handling - Resolve issues
    5. Funding Preparation - Prepare for disbursement
    6. Communication - Keep borrower informed
    """
    
    def __init__(self, loan_file: LoanFile, verbose: bool = True):
        """
        Initialize the Loan Operations Crew.
        
        Args:
            loan_file: The LoanFile object containing loan details
            verbose: Whether to print detailed agent outputs
        """
        self.loan_file = loan_file
        self.verbose = verbose
        self._setup_agents()
        self._setup_tasks()
    
    def _setup_agents(self):
        """Create all agents for the crew."""
        self.document_tracker = create_document_tracker_agent()
        self.verification_agent = create_verification_agent()
        self.compliance_checker = create_compliance_checker_agent()
        self.exception_handler = create_exception_handler_agent()
        self.funding_coordinator = create_funding_coordinator_agent()
        self.communication_agent = create_communication_agent()
    
    def _get_loan_context(self) -> str:
        """Generate loan context string for tasks."""
        docs_status = {}
        for name, doc in self.loan_file.documents.items():
            docs_status[name] = {
                "status": doc.status.value,
                "received_date": doc.received_date,
            }
        
        return f"""
Loan ID: {self.loan_file.loan_id}
Borrower: {self.loan_file.borrower_name}
Email: {self.loan_file.borrower_email}
Phone: {self.loan_file.borrower_phone}

Loan Type: {self.loan_file.loan_type}
Loan Amount: ${self.loan_file.loan_amount:,.2f}
Interest Rate: {self.loan_file.interest_rate}%
Term: {self.loan_file.term_months} months

Approval Date: {self.loan_file.approval_date}
Approval Conditions: {', '.join(self.loan_file.approval_conditions) or 'None'}
Target Funding Date: {self.loan_file.target_funding_date or 'TBD'}
Current Status: {self.loan_file.funding_status.value}

Documents Status:
{json.dumps(docs_status, indent=2)}

Active Exceptions: {len([e for e in self.loan_file.exceptions if not e.resolved_date])}
"""
    
    def _get_communication_needs(self) -> str:
        """Determine what communications are needed."""
        needs = []
        
        # Check for missing documents
        missing_docs = [name for name, doc in self.loan_file.documents.items() 
                       if doc.status.value in ["pending", "expired"]]
        if missing_docs:
            needs.append(f"Document request needed for: {', '.join(missing_docs)}")
        
        # Check for unresolved exceptions
        active_exceptions = [e for e in self.loan_file.exceptions if not e.resolved_date]
        if active_exceptions:
            needs.append(f"Exception notices needed: {len(active_exceptions)} active exceptions")
        
        # General status update
        needs.append("General status update on loan progress")
        
        return "\n".join(needs) if needs else "Standard status update only"
    
    def _setup_tasks(self):
        """Create all tasks for the crew."""
        loan_context = self._get_loan_context()
        communication_needs = self._get_communication_needs()
        
        # Sequential task chain
        self.document_tracking_task = create_document_tracking_task(
            self.document_tracker, loan_context
        )
        
        self.verification_task = create_verification_task(
            self.verification_agent, loan_context
        )
        self.verification_task.context = [self.document_tracking_task]
        
        self.compliance_task = create_compliance_review_task(
            self.compliance_checker, loan_context
        )
        self.compliance_task.context = [self.document_tracking_task, self.verification_task]
        
        self.exception_task = create_exception_handling_task(
            self.exception_handler, loan_context
        )
        self.exception_task.context = [
            self.document_tracking_task, 
            self.verification_task, 
            self.compliance_task
        ]
        
        self.funding_task = create_funding_preparation_task(
            self.funding_coordinator, loan_context
        )
        self.funding_task.context = [
            self.verification_task, 
            self.compliance_task, 
            self.exception_task
        ]
        
        self.communication_task = create_communication_task(
            self.communication_agent, loan_context, communication_needs
        )
        self.communication_task.context = [
            self.document_tracking_task,
            self.exception_task,
            self.funding_task
        ]
    
    def create_crew(self) -> Crew:
        """Create and return the configured crew."""
        return Crew(
            agents=[
                self.document_tracker,
                self.verification_agent,
                self.compliance_checker,
                self.exception_handler,
                self.funding_coordinator,
                self.communication_agent,
            ],
            tasks=[
                self.document_tracking_task,
                self.verification_task,
                self.compliance_task,
                self.exception_task,
                self.funding_task,
                self.communication_task,
            ],
            process=Process.sequential,
            verbose=self.verbose,
        )
    
    def run(self) -> str:
        """
        Execute the loan operations workflow.
        
        Returns:
            The final output from the crew execution
        """
        crew = self.create_crew()
        result = crew.kickoff()
        return result


def process_loan_file(loan_file_path: str, verbose: bool = True) -> str:
    """
    Process a single loan file through the operations workflow.
    
    Args:
        loan_file_path: Path to the loan file JSON
        verbose: Whether to show detailed output
        
    Returns:
        Processing results
    """
    loan_file = LoanFile.from_json(loan_file_path)
    crew = LoanOperationsCrew(loan_file, verbose=verbose)
    return crew.run()
