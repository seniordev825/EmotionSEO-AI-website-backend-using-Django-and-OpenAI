from openai import OpenAI
import os
from dotenv import load_dotenv 
load_dotenv()
#api_key = os.getenv('OPENAI_KEY')
client = OpenAI(api_key = api_key)

 
 
  
prompt = f'''Write text. The text must be SEO-Optmized Content and the text must be included {keywords}
        The text must be written with {emotion}.
        The title of text must be "{title}" and don't change or add anything and write with bigger font than content!
        We want this content to be high searchable.
        Write the text naturally and avoid comments or words(for example: SEO-Optimized Content) that are not related to the topic.
        Don't involve unnecessary symbols such as ---, ###, **, and so on.
        Add line breaks, dashes and indentations to make the text easy to read and understand.
        Must consider to accurately distinguish between title, content, paragraphes and so on.
        Write the new sentences on the new rows.'''

res=client.chat.completions.create(
        model = "gpt-4-1106-preview",
        messages = [
            {"role": "system", "content": 'You write text based on my prompt.'
            },
            {"role": "user", "content": prompt},
        ]
    )
content = res.choices[0].message.content

print(content)

