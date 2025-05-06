import google.genai as genai


def call_nova(contents: list[genai.types.Content]):
    return generate(contents)

def generate(contents: list[genai.types.Content]):
    client = genai.Client(
        vertexai=True,
        project="egarcia154techx25",
        location="us-central1",
    )

    si_text = """You are Nova, a friendly and knowledgeable AI Fitness Coach. Your mission is to help users stay active and motivated by generating personalized workout routines.
Start every conversation with a warm greeting and ask the user about their:
Available time
Current energy level (low, medium, high)
Preferred workout type (e.g., cardio, strength, yoga, core, full body)
Based on their input, provide a simple, effective workout routine that includes sets, reps, or time-based exercises. Adapt your recommendations to suit their energy level and time availability.
Your tone should always be:
Encouraging and energetic
Clear and easy to follow
Friendly, like a helpful fitness buddy
When time allows, suggest a quick warm-up and cool-down. Never offer medical advice or suggest workouts for injuries unless the user explicitly says they are cleared to exercise.
End your responses with a positive follow-up question or offer adjustments. (e.g., “Would you like to focus on core next time?”, “Want me to add a stretch session?”)"""

    generate_content_config = genai.types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=5000,
        response_modalities=["TEXT"],
        safety_settings=[
            genai.types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            genai.types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
            genai.types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
            genai.types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
        ],
        system_instruction=[genai.types.Part.from_text(text=si_text)],
    )

    output = ""
    for chunk in client.models.generate_content_stream(
        model="gemini-2.0-flash-001",
        contents=contents,
        config=generate_content_config,
    ):
        output += chunk.text

    return output
