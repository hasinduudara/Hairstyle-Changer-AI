import gradio as gr
from PIL import Image

def generate_single_style(image, style_prompt):
    # TODO: In Step 4, we will connect the Hugging Face AI Model here.
    # For now, it just returns a resized version of the original image 
    # to simulate the process without crashing.
    return image.copy()

def create_2x2_grid(img1, img2, img3, img4):
    # Set standard size for each generated image
    target_size = (512, 512)
    
    # Resize all images to ensure they fit perfectly in the grid
    i1 = img1.resize(target_size)
    i2 = img2.resize(target_size)
    i3 = img3.resize(target_size)
    i4 = img4.resize(target_size)
    
    # Create a new blank canvas (1024x1024) to hold all 4 images
    grid_width = target_size[0] * 2
    grid_height = target_size[1] * 2
    grid = Image.new('RGB', (grid_width, grid_height))
    
    # Paste the images into their respective grid positions
    grid.paste(i1, (0, 0))                           # Top-Left
    grid.paste(i2, (target_size[0], 0))              # Top-Right
    grid.paste(i3, (0, target_size[1]))              # Bottom-Left
    grid.paste(i4, (target_size[0], target_size[1])) # Bottom-Right
    
    return grid

def process_hairstyles(user_image):
    # Define 4 different styles to generate
    style1 = generate_single_style(user_image, "short buzz cut")
    style2 = generate_single_style(user_image, "classic pompadour")
    style3 = generate_single_style(user_image, "long wavy hair")
    style4 = generate_single_style(user_image, "curly layered cut")
    
    # Combine the 4 images into a single 2x2 grid
    final_grid = create_2x2_grid(style1, style2, style3, style4)
    
    return final_grid

# Gradio UI Layout
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# ✂️ Smart Hairstyle Changer AI")
    gr.Markdown("Upload a clear photo of your face to see 4 different hairstyle recommendations.")
    
    with gr.Row():
        with gr.Column():
            input_image = gr.Image(label="Upload your photo here", type="pil")
            submit_btn = gr.Button("Generate Styles 🚀", variant="primary")
        
        with gr.Column():
            output_image = gr.Image(label="Result (4 Styles)")
    
    # Bind the new processing function to the button click
    submit_btn.click(
        fn=process_hairstyles, 
        inputs=input_image, 
        outputs=output_image
    )

if __name__ == "__main__":
    demo.launch()