import os
import gradio as gr
from PIL import Image
import requests
import io
import base64

# Retrieve the Hugging Face token securely from environment variables
HF_TOKEN = os.getenv("HF_TOKEN")

# Instruct-Pix2Pix API endpoint
API_URL = "https://api-inference.huggingface.co/models/timbrooks/instruct-pix2pix"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def query_hf_api(image, prompt):
    # Convert PIL image to Base64 string for the API payload
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    encoded_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    
    # JSON structure required by Hugging Face multimodal models
    payload = {
        "inputs": prompt,
        "image": encoded_image
    }
    
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            # Convert the returned binary data back to a PIL Image
            return Image.open(io.BytesIO(response.content))
        else:
            print(f"API Error ({response.status_code}): {response.text}")
            # Fallback: Return original image if API fails (e.g. rate limit)
            return image.copy()
    except Exception as e:
        print(f"Request failed: {e}")
        return image.copy()

def generate_single_style(image, style_prompt):
    # Make the prompt more descriptive for better AI generation
    full_prompt = f"change hairstyle to {style_prompt}, highly detailed, realistic"
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
    # Note: Free tier API might take 10-20 seconds per image. 
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