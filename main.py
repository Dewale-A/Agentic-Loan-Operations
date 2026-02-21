#!/usr/bin/env python3
"""
AgenticLoanOperations - Post-Approval Back Office Automation

This system automates the loan operations workflow from approval to funding,
using a team of specialized AI agents to handle document collection,
verification, compliance review, exception handling, and borrower communication.

Usage:
    python main.py                              # Process all loan files
    python main.py --loan LOAN001.json          # Process specific loan
    python main.py --loan LOAN001.json --quiet  # Minimal output
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.settings import SAMPLE_LOANS_DIR, OUTPUT_DIR
from src.crew import LoanOperationsCrew, process_loan_file
from src.models.loan_file import LoanFile


def print_banner():
    """Print application banner."""
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║     █████╗  ██████╗ ███████╗███╗   ██╗████████╗██╗ ██████╗                   ║
║    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██║██╔════╝                   ║
║    ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   ██║██║                        ║
║    ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ██║██║                        ║
║    ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ██║╚██████╗                   ║
║    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝ ╚═════╝                   ║
║                                                                               ║
║              L O A N   O P E R A T I O N S   S Y S T E M                     ║
║                    Post-Approval Back Office Automation                       ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  Agents:                                                                      ║
║    📋 Document Tracker    → Track & chase missing documents                   ║
║    ✓  Verification Agent → Verify document authenticity                      ║
║    ⚖  Compliance Checker → Final compliance review                           ║
║    ⚠  Exception Handler  → Resolve issues & exceptions                       ║
║    💰 Funding Coordinator → Prepare disbursement                             ║
║    📧 Communication Agent → Borrower updates                                 ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)


def list_loan_files() -> list:
    """List available loan files in the sample directory."""
    loan_dir = Path(SAMPLE_LOANS_DIR)
    if not loan_dir.exists():
        return []
    return list(loan_dir.glob("*.json"))


def process_single_loan(loan_path: str, verbose: bool = True) -> dict:
    """
    Process a single loan file.
    
    Args:
        loan_path: Path to the loan JSON file
        verbose: Whether to show detailed output
        
    Returns:
        Processing results dictionary
    """
    print(f"\n{'='*60}")
    print(f"Processing: {loan_path}")
    print(f"{'='*60}\n")
    
    start_time = datetime.now()
    
    try:
        loan_file = LoanFile.from_json(loan_path)
        
        print(f"Loan ID: {loan_file.loan_id}")
        print(f"Borrower: {loan_file.borrower_name}")
        print(f"Amount: ${loan_file.loan_amount:,.2f}")
        print(f"Type: {loan_file.loan_type}")
        print(f"Status: {loan_file.funding_status.value}")
        print()
        
        # Create and run the crew
        crew = LoanOperationsCrew(loan_file, verbose=verbose)
        result = crew.run()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Save results
        output_dir = Path(OUTPUT_DIR)
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"{loan_file.loan_id}_operations_report.md"
        with open(output_file, 'w') as f:
            f.write(f"# Loan Operations Report: {loan_file.loan_id}\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Processing Time:** {duration:.1f} seconds\n\n")
            f.write("---\n\n")
            f.write(str(result))
        
        print(f"\n{'='*60}")
        print(f"✅ Processing Complete")
        print(f"   Duration: {duration:.1f} seconds")
        print(f"   Report: {output_file}")
        print(f"{'='*60}\n")
        
        return {
            "loan_id": loan_file.loan_id,
            "status": "success",
            "duration": duration,
            "output_file": str(output_file),
            "result": str(result),
        }
        
    except Exception as e:
        print(f"\n❌ Error processing loan: {e}")
        return {
            "loan_id": loan_path,
            "status": "error",
            "error": str(e),
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AgenticLoanOperations - Post-Approval Back Office Automation"
    )
    parser.add_argument(
        "--loan", "-l",
        help="Specific loan file to process (filename in sample_loans/)",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Minimal output (less verbose)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available loan files",
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # List mode
    if args.list:
        loan_files = list_loan_files()
        if loan_files:
            print("Available loan files:")
            for f in loan_files:
                print(f"  - {f.name}")
        else:
            print(f"No loan files found in {SAMPLE_LOANS_DIR}/")
            print("Add JSON loan files to get started.")
        return
    
    # Process specific loan
    if args.loan:
        loan_path = Path(SAMPLE_LOANS_DIR) / args.loan
        if not loan_path.exists():
            print(f"Error: Loan file not found: {loan_path}")
            sys.exit(1)
        
        result = process_single_loan(str(loan_path), verbose=not args.quiet)
        
        if result["status"] == "error":
            sys.exit(1)
        return
    
    # Process all loan files
    loan_files = list_loan_files()
    if not loan_files:
        print(f"No loan files found in {SAMPLE_LOANS_DIR}/")
        print("\nTo get started:")
        print("  1. Add loan JSON files to the sample_loans/ directory")
        print("  2. Run: python main.py --loan YOUR_LOAN.json")
        print("\nOr use the sample files if available:")
        print("  python main.py --list")
        return
    
    print(f"Found {len(loan_files)} loan file(s) to process\n")
    
    results = []
    for loan_path in loan_files:
        result = process_single_loan(str(loan_path), verbose=not args.quiet)
        results.append(result)
    
    # Summary
    print("\n" + "="*60)
    print("PROCESSING SUMMARY")
    print("="*60)
    
    success = [r for r in results if r["status"] == "success"]
    errors = [r for r in results if r["status"] == "error"]
    
    print(f"Total Processed: {len(results)}")
    print(f"Successful: {len(success)}")
    print(f"Errors: {len(errors)}")
    
    if errors:
        print("\nFailed loans:")
        for r in errors:
            print(f"  - {r['loan_id']}: {r.get('error', 'Unknown error')}")
    
    print()


if __name__ == "__main__":
    main()
