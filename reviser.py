
def revise(md_text: str,
                                        previous_examples_json,
                                        previous_prompt_text,
                                        sanity_report_json) -> dict:
    from openai import OpenAI
    import json
    from generator import load_prompt
    import os
    from dotenv import load_dotenv
    load_dotenv()

    client = OpenAI(api_key=os.environ.get('KEY'))

    # Load prompt from YAML file
    prompt = load_prompt('langextract_reviser',
                        md_text=md_text,
                        previous_examples_json=previous_examples_json,
                        previous_prompt_text=previous_prompt_text,
                        sanity_report_json=sanity_report_json)

    
    messages=[{"role": "user", "content": prompt}]
    completion = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        response_format={"type": "json_object"}
    )

    json_str = completion.choices[0].message.content
    return json.loads(json_str),messages
