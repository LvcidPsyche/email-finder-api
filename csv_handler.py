"""
CSV import/export utilities for bulk email operations.
"""
import csv
import io
from typing import List, Dict
from pydantic import BaseModel


class CSVNameEntry(BaseModel):
    first_name: str
    last_name: str
    domain: str = None


def parse_csv_upload(csv_content: str, has_domain_column: bool = False) -> List[Dict]:
    """
    Parse uploaded CSV content.

    Expected formats:
    - With domain: first_name, last_name, domain
    - Without domain: first_name, last_name (domain provided separately)

    Returns:
        List of dicts with first_name, last_name, domain (if present)
    """
    reader = csv.DictReader(io.StringIO(csv_content))
    entries = []

    for row in reader:
        # Clean and validate
        first_name = row.get('first_name', '').strip()
        last_name = row.get('last_name', '').strip()
        domain = row.get('domain', '').strip() if has_domain_column else None

        if not first_name or not last_name:
            continue  # Skip invalid rows

        entries.append({
            'first_name': first_name,
            'last_name': last_name,
            'domain': domain
        })

    return entries


def export_results_to_csv(results: List[Dict]) -> str:
    """
    Export email finding results to CSV format.

    Args:
        results: List of result dicts from bulk_find or similar

    Returns:
        CSV string ready for download
    """
    output = io.StringIO()
    fieldnames = [
        'first_name',
        'last_name',
        'domain',
        'top_email',
        'pattern',
        'confidence',
        'all_emails'
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for result in results:
        person = result.get('person', {})
        emails = result.get('emails', [])
        domain = result.get('domain', '')

        if emails:
            top_email = emails[0]  # Highest confidence
            all_emails_str = '; '.join([e['email'] for e in emails])

            writer.writerow({
                'first_name': person.get('first_name', ''),
                'last_name': person.get('last_name', ''),
                'domain': domain,
                'top_email': top_email.get('email', ''),
                'pattern': top_email.get('pattern', ''),
                'confidence': top_email.get('confidence', ''),
                'all_emails': all_emails_str
            })
        else:
            writer.writerow({
                'first_name': person.get('first_name', ''),
                'last_name': person.get('last_name', ''),
                'domain': domain,
                'top_email': 'N/A',
                'pattern': 'N/A',
                'confidence': 'N/A',
                'all_emails': 'N/A'
            })

    return output.getvalue()


def export_verification_results_to_csv(results: List[Dict]) -> str:
    """
    Export SMTP verification results to CSV.

    Args:
        results: List of verification result dicts

    Returns:
        CSV string
    """
    output = io.StringIO()
    fieldnames = [
        'email',
        'exists',
        'deliverable',
        'catch_all',
        'mx_host',
        'error'
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for result in results:
        writer.writerow({
            'email': result.get('email', ''),
            'exists': result.get('exists', ''),
            'deliverable': result.get('deliverable', ''),
            'catch_all': result.get('catch_all', ''),
            'mx_host': result.get('mx_host', ''),
            'error': result.get('error', '')
        })

    return output.getvalue()
