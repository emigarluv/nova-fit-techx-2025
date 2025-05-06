import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/key.json"
from google import genai as genai 
from google.cloud import bigquery
from datetime import date

project_id = "egarcia154techx25"
dataset_id = "ISE"

def generate_content(user_id):
    name, age = get_name_age(user_id)
    if not name or not age:
        return "User not found or incomplete data."
    content = generate(name, age)
    return content

def get_name_age(user_id):
    bigquery_client = bigquery.Client(project=project_id)
    
    query = """
        SELECT Name, DateOfBirth
        FROM `egarcia154techx25.ISE.Users`
        WHERE UserId = @user_id
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )

    query_job = bigquery_client.query(query, job_config=job_config)
    result = query_job.result()
    rows = list(result)

    if not rows:
        return None, None

    row = rows[0]
    name = row["Name"]
    birth_year = row["DateOfBirth"].year
    current_year = date.today().year
    age = current_year - birth_year

    return name, age

def generate(user_name, user_age):
    client = genai.Client(
        vertexai=True,
        project="egarcia154techx25",
        location="us-central1",
    )

    prompt = f"""Generate a short (one sentence) and motivational piece of wellness advice for a fitness app user. Focus on encouragement and healthy habits. Avoid technical language and keep the tone friendly and supportive.

User Info:
- Name: {user_name}
- Age: {user_age}

Use this information to provide a relevant and uplifting wellness tip."""

    system_instruction = """You are a friendly and knowledgeable wellness assistant embedded in a fitness tracking app. Your goal is to provide users with personalized, motivational, and actionable advice related to health, fitness, and overall well-being.
Tailor your responses based on available user data (e.g., activity type, frequency, goals, or recent performance). Keep your tone encouraging, clear, and non-judgmental. Your advice should be helpful whether the user is a beginner or an experienced athlete."""

    contents = [
        genai.types.Content(
            role="user",
            parts=[genai.types.Part.from_text(text=prompt)]
        )
    ]

    config = genai.types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=250,
        response_modalities=["TEXT"],
        safety_settings=[
            genai.types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            genai.types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
            genai.types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
            genai.types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
        ],
        system_instruction=[genai.types.Part.from_text(text=system_instruction)],
    )

    output = ""
    for chunk in client.models.generate_content_stream(
        model="gemini-2.0-flash-001",
        contents=contents,
        config=config,
    ):
        output += chunk.text

    return output


