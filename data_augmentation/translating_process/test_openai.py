import os
from openai import OpenAI

"""
set an environment variable in your shell by adding the following line 
to .bashrc, .bash_profile, or .zshrc file:
export OPENAI_API_KEY=your_openai_api_key_here
Again, replace your_openai_api_key_here with your actual API key. 
After adding this line, you may need to restart your terminal or 
source the file (e.g., source ~/.bashrc).
"""

"""
Sample Prompt:
Act as a Knowledge Base, generate top k related paragraphs to this input sentence: "kingdom hospital, lewiston from stephen king miniseries of the same name".
With `k = 3`.
The result need to be stricly in form of a python list like this: `["para_1", "para_2", ..., "para_k"]`, where `para_k` is the k_th retrived paragraph.
Just generate the result, no need explanation.
"""

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(model=model,
    messages=messages,
    temperature=0)
    return response.choices[0].message.content

def GPTtranslate(entity, from_lang, to_lang):
    prompt = f"""
        Your task is to translate this entity: '{entity}'
        from languague '{from_lang}' to language '{to_lang}'
        The result need to be stricly lower case and have no extra spaces.
        Just generate the result, no need explanation.
    """
    response = get_completion(prompt)
    return response.strip().replace('\u200d', '').replace('\u200c', '').replace('\u200b', '')