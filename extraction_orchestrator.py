"""
Invoice Extraction Pipeline Orchestrator

Pipeline:
1. Generate initial examples + prompt from invoice
2. Validate with sanity checker
3. Revise if needed (iterative improvement)
4. Extract using LangExtract with final prompt + examples
"""

from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from generator import generate_invoice_langextract_assets
from sanity import sanity_check
from reviser import revise
from lx import extract
import json


def run_extraction_pipeline(invoice_markdown: str, max_revisions: int = 3, verbose: bool = True):
    """
    Run the complete extraction pipeline on an invoice.

    Args:
        invoice_markdown: Raw invoice text in markdown format
        max_revisions: Maximum number of revision iterations
        verbose: Print progress logs

    Returns:
        AnnotatedDocument: Final extraction result from LangExtract
    """

    # Step 1: Generate initial dataset
    if verbose:
        print("Step 1: Generating initial examples and prompt...")

    generation_result, _ = generate_invoice_langextract_assets(invoice_markdown)
    examples = generation_result['extractions']
    prompt = generation_result['prompt']

    if verbose:
        print(f"  Generated {len(examples)} examples")

    # Step 2-3: Iterative improvement with sanity checking
    for iteration in range(max_revisions):
        if verbose:
            print(f"\nIteration {iteration + 1}/{max_revisions}")
            print("  Running sanity check...")

        # Sanity check current examples
        sanity_result = sanity_check(
            data={'extractions': examples, 'prompt': prompt},
            original_md=invoice_markdown
        )

        if verbose:
            print(f"  Valid: {sanity_result['is_valid']}")
            if not sanity_result['is_valid']:
                error_count = sum([
                    len(sanity_result.get('schema_errors', [])),
                    len(sanity_result.get('hallucinations', [])),
                    len(sanity_result.get('missing_values', [])),
                    len(sanity_result.get('mismatches', [])),
                    len(sanity_result.get('logical_errors', []))
                ])
                print(f"  Found {error_count} issues")

        # If valid, stop iterating
        if sanity_result['is_valid']:
            if verbose:
                print("  Quality check passed!")
            break

        # Revise to fix issues
        if verbose:
            print("  Revising examples and prompt...")

        revision_result, _ = revise(
            md_text=invoice_markdown,
            previous_examples_json=json.dumps(examples, indent=2),
            previous_prompt_text=prompt,
            sanity_report_json=json.dumps(sanity_result, indent=2)
        )

        examples = revision_result['extractions']
        prompt = revision_result['prompt']

        if verbose:
            print(f"  Updated to {len(examples)} examples")

    # Step 4: Extract using LangExtract
    if verbose:
        print("\nStep 4: Running LangExtract extraction...")

    result = extract(
        invoice_text=invoice_markdown,
        prompt=prompt,
        examples=examples
    )

    if verbose:
        print(f"  Extraction complete!")
        print(f"  Found {len(result.extractions)} extractions")

    return result


def extract_invoice(invoice_markdown: str, **kwargs):
    """Convenience function for simple extraction."""
    return run_extraction_pipeline(invoice_markdown, **kwargs)


