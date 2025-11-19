from openai import OpenAI
import json, os
from dotenv import load_dotenv

def sanity_check(data, original_md):
    """
    Deep sanity check comparing extracted data vs original markdown invoice.
    """
    load_dotenv()
    from generator import load_prompt

    client = OpenAI(api_key=os.environ.get('KEY'))

    data_str = json.dumps(data, indent=2, default=str)

    prompt = load_prompt('sanity_checker',
                        original_md=original_md,
                        data_str=data_str)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a strict data validation engine."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)


