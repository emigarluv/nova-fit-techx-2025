import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/key.json"

from vertexai.preview.vision_models import ImageGenerationModel
import vertexai
import base64
from io import BytesIO

# Initialize Vertex AI
vertexai.init(project="egarcia154techx25", location="us-central1")

# Load the image generation model
def generate_motivational_image():
    generation_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")

    # Generate the image
    images = generation_model.generate_images(
        prompt="Generate a motivational, high-resolution image for a wellness app. The scene should be cinematic and uplifting, set in inspiring environments such as natural landscapes, outdoor street runs, gym settings, or athletic spaces. Emphasize emotion, movement, and the connection between the individual and their surroundings. Avoid using text, logos, or brand-specific elements. The focus should be on powerful, expressive imagery — not hyper-realistic portraits — that visually inspires action and well-being.",
        number_of_images=1,
        aspect_ratio="4:3",
        negative_prompt="",
        person_generation="",
        safety_filter_level="",
        add_watermark=True,
    )

    # Convert to base64
    buffered = BytesIO()
    images[0]._pil_image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return img_base64
