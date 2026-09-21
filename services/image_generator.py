import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient


load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

client = InferenceClient(
    token=HF_TOKEN
)


def generate_outfit_image(prompt, output_path):
    """
    Generate an outfit image using Hugging Face
    and save it to the specified path.
    """

    if not HF_TOKEN:
        raise ValueError("HF_TOKEN is not configured in .env")

    image = client.text_to_image(
        prompt=prompt,
        model="black-forest-labs/FLUX.1-schnell"
    )

    image.save(output_path)

    return output_path