from PIL import Image, ImageDraw, ImageFont
import textwrap

def create_overlay(title, verse, reflection, output_path):
    # HD Canvas (Transparent)
    img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Text config
    margin = 100
    width = 1920
    height = 1080
    
    # Use default font (or try to find a system one)
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
        font_verse = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
        font_ref = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 35)
    except:
        font_title = ImageFont.load_default()
        font_verse = ImageFont.load_default()
        font_ref = ImageFont.load_default()

    # Wrapped reflection
    wrapper = textwrap.TextWrapper(width=60)
    ref_lines = wrapper.wrap(text=reflection)
    ref_text = "\n".join(ref_lines)
    
    # Draw Background Box (Semi-transparent)
    # Positioning at the bottom
    box_height = 250
    draw.rectangle([margin, height - box_height - 50, width - margin, height - 50], fill=(0, 0, 0, 150))
    
    # Draw Text
    draw.text((width/2, height - box_height + 10), title, font=font_title, fill="white", anchor="mm")
    draw.text((width/2, height - box_height + 70), verse, font=font_verse, fill="white", anchor="mm")
    
    # Draw Reflection lines
    y_offset = height - box_height + 130
    for line in ref_lines:
        draw.text((width/2, y_offset), line, font=font_ref, fill="white", anchor="mm")
        y_offset += 45

    img.save(output_path)

create_overlay(
    "EL SUEÑO DE JOSÉ", 
    "Mateo 1:20", 
    "Dios interviene en tus sueños cuando la lógica ya no tiene respuestas. Confía en Su plan silencioso.",
    "/Users/hjalmarmeza/Downloads/Antigravity/scratch/text_overlay.png"
)
