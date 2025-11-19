def load_prompt(prompt_name: str, **kwargs) -> str:
    """Load and format a prompt template from prompts.yml"""
    import yaml
    from pathlib import Path

    prompts_path = Path(__file__).parent / "prompts.yml"
    with open(prompts_path, 'r') as f:
        prompts_data = yaml.safe_load(f)

    prompt_config = prompts_data['prompts'][prompt_name]
    template = prompt_config['template']

    return template.format(**kwargs)


def generate_invoice_langextract_assets(md_text: str) -> dict:
    from openai import OpenAI
    import json
    import os
    from dotenv import load_dotenv
    load_dotenv() 

    client = OpenAI(api_key=os.environ.get('KEY'))

    # Load prompt from YAML file
    prompt = load_prompt('invoice_langextract', md_text=md_text)
    
    messages=[{"role": "user", "content": prompt}]
    completion = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        response_format={"type": "json_object"}
    )

    json_str = completion.choices[0].message.content
    return json.loads(json_str),messages
