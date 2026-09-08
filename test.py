import requests

endpoint = "https://my-foundry-resource-dan01.openai.azure.com/openai/deployments/gpt-5-mini-deployment/chat/completions?api-version=2024-10-21"

headers = {

    "Content-Type": "application/json",

    "api-key": "5tmHfhE7u8FYUzeaBRzapU6LuIlhnU0wKbUJPXPiBKC9mP6MUTkgJQQJ99CIACL93NaXJ3w3AAAAACOGkDdJ"

}

payload = {

    "messages": [

        {

            "role": "system",

            "content": (

                "You are a resume tailoring assistant. Given a resume and a job description, "

                "rewrite the resume bullet points to align with the job description while "

                "preserving factual accuracy. Do not invent experience, skills, or metrics "

                "that aren't in the original resume. Return valid JSON only, in this shape: "

                '{"changes": [{"original": "...", "tailored": "...", "reasoning": "..."}]}'

            )

        },

        {

            "role": "user",

            "content": "RESUME:\n<paste resume text>\n\nJOB DESCRIPTION:\n<paste JD text>"

        }

    ],

    "max_completion_tokens": 2000

}

response = requests.post(endpoint, headers=headers, json=payload)

print(response.json()["choices"][0]["message"]["content"])