import os
from dotenv import load_dotenv
load_dotenv()
import gradio as gr
from PIL import Image
from huggingface_hub import InferenceClient
import io

# Retrieve the Hugging Face token securely from environment variables
HF_TOKEN = os.getenv("HF_TOKEN")

# Using Inference Providers (fal-ai) via huggingface_hub client
# api-inference.huggingface.co is deprecated; instruct-pix2pix has no active provider
client = InferenceClient(
    provider="fal-ai",
    api_key=HF_TOKEN,
)

MODEL = "black-forest-labs/FLUX.1-Kontext-dev"

def query_hf_api(image, prompt):
    # Convert PIL image to bytes for the API payload
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    image_bytes = img_byte_arr.getvalue()

    try:
        result = client.image_to_image(
            image_bytes,
            prompt=prompt,
            model=MODEL,
        )
        # result is already a PIL.Image
        return result
    except Exception as e:
        print(f"Request failed: {e}")
        # Fallback: Return original image if API fails
        return image.copy()

def generate_single_style(image, style_prompt):
    # Make the prompt more descriptive for better AI generation
    full_prompt = f"change hairstyle to {style_prompt}, highly detailed, realistic, keep the same face and person"
    return query_hf_api(image, full_prompt)

def create_2x2_grid(img1, img2, img3, img4):
    target_size = (512, 512)
    i1, i2, i3, i4 = [img.resize(target_size) for img in (img1, img2, img3, img4)]

    grid_width = target_size[0] * 2
    grid_height = target_size[1] * 2
    grid = Image.new('RGB', (grid_width, grid_height))

    grid.paste(i1, (0, 0))
    grid.paste(i2, (target_size[0], 0))
    grid.paste(i3, (0, target_size[1]))
    grid.paste(i4, (target_size[0], target_size[1]))

    return grid

def process_hairstyles(user_image):
    # Generate 4 different styles
    # Note: each call goes through fal-ai; may take a few seconds per image.
    style1 = generate_single_style(user_image, "short buzz cut")
    style2 = generate_single_style(user_image, "classic pompadour")
    style3 = generate_single_style(user_image, "long wavy hair")
    style4 = generate_single_style(user_image, "curly layered cut")

    return create_2x2_grid(style1, style2, style3, style4)

with gr.Blocks() as demo:
    gr.Markdown("# ✂️ Smart Hairstyle Changer AI")
    gr.Markdown("Upload a clear photo of your face to see 4 different hairstyle recommendations.")

    with gr.Row():
        with gr.Column():
            input_image = gr.Image(label="Upload your photo here", type="pil")
            submit_btn = gr.Button("Generate Styles 🚀", variant="primary")

        with gr.Column():
            output_image = gr.Image(label="Result (4 Styles)")

    submit_btn.click(
        fn=process_hairstyles,
        inputs=input_image,
        outputs=output_image
    )

if __name__ == "__main__":
    # Gradio 6.0 standard for passing theme
    demo.launch(theme=gr.themes.Soft())