def _convert_to_example_data(data, invoice_text):
    """Convert dict/list examples to lx.data.ExampleData objects

    Args:
        data: List of extraction dicts OR list of example dicts with 'text' field
        invoice_text: The invoice text to use if examples don't have 'text' field
    """
    import langextract as lx
    import json

    # Handle JSON string
    if isinstance(data, str):
        data = json.loads(data)

    # Handle single dict
    if isinstance(data, dict):
        data = [data]

    # Check if this is a list of extraction objects (from generator)
    # or a list of full example objects (with 'text' field)
    if data and "text" not in data[0] and "extraction_class" in data[0]:
        # This is a list of extraction objects - wrap them in a single ExampleData
        extractions = []
        for ext in data:
            extractions.append(
                lx.data.Extraction(
                    extraction_class=ext["extraction_class"],
                    extraction_text=ext["extraction_text"],
                    attributes=ext.get("attributes", {})
                )
            )
        return [lx.data.ExampleData(text=invoice_text, extractions=extractions)]

    # Otherwise, this is a list of full example objects
    examples = []
    for item in data:
        extractions = []
        for ext in item.get("extractions", []):
            extractions.append(
                lx.data.Extraction(
                    extraction_class=ext["extraction_class"],
                    extraction_text=ext["extraction_text"],
                    attributes=ext.get("attributes", {})
                )
            )

        example = lx.data.ExampleData(
            text=item.get("text", invoice_text),
            extractions=extractions
        )
        examples.append(example)

    return examples


def extract(invoice_text: str, prompt: str, examples: str) -> dict:
    import langextract as lx
    import os

    from dotenv import load_dotenv
    load_dotenv()

    # Convert dict/list examples to ExampleData objects
    if isinstance(examples, (list, dict, str)):
        examples = _convert_to_example_data(examples, invoice_text)

    result = lx.extract(
        text_or_documents=invoice_text,
        prompt_description=prompt,
        examples=examples,
        model_id="gpt-4o",
        api_key=os.environ.get('KEY'),
        fence_output=True,
        use_schema_constraints=False,
        max_char_buffer=2000,
        batch_length=10,
        max_workers=10,
        extraction_passes=3
    )
    return result
