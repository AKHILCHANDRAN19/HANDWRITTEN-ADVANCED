from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
import os
import re

# Directory containing font files
font_dir = "fonts"

# Map user input to font file names
font_files = {
    "1": "ShadowsIntoLight-Regular.ttf",
    "2": "Satisfy-Regular.ttf",
    "3": "Caveat-Regular.ttf",
    "4": "PatrickHand-Regular.ttf",
    "5": "ReenieBeanie-Regular.ttf",
    "6": "Sacramento-Regular.ttf",
    "7": "HomemadeApple-Regular.ttf"
}

# Display font options to the user
print("Choose a font:")
for key, value in font_files.items():
    print(f"{key}. {value.split('-')[0]}")

# Get the user's choice for font
user_choice = input("Enter the number corresponding to your choice: ")

if user_choice not in font_files:
    print("Invalid choice. Please select a number between 1 and 7.")
else:
    font_name = font_files[user_choice]
    font_path = os.path.join(font_dir, font_name)

    if not os.path.exists(font_path):
        print(f"Font file {font_name} not found in the {font_dir} folder.")
    else:
        # Register the font
        pdfmetrics.registerFont(TTFont('CustomFont', font_path))

        # Get the color choice from the user
        print("Choose a pen color:")
        print("1. Black")
        print("2. Blue")
        color_choice = input("Enter the number corresponding to your choice: ")

        pen_color = (0, 0, 0) if color_choice == "1" else (0, 0, 1) if color_choice == "2" else (0, 0, 0)

        # Get the text input from the user
        print("Enter the text to convert to PDF (End input with a single line containing 'END'):")
        text_lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            text_lines.append(line)
        text_to_convert = "\n".join(text_lines)

        # Create PDF
        pdf_filename = "user_text_handwritten.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=letter)
        width, height = letter

        # Set font and size (increased)
        font_size = 16
        c.setFont('CustomFont', font_size)

        # Set margins (4 cm on all sides)
        margin = 4 * inch / 2.54
        text_width = width - 2*margin
        text_height = height - 2*margin

        # Function to draw text within borders
        def draw_text_in_border(canvas, text, x, y, width, height):
            # Draw border
            canvas.setStrokeColorRGB(0.5, 0.5, 0.5)  # Light gray color for border
            canvas.setLineWidth(1)
            canvas.rect(x, y, width, height)

            # Set text color
            canvas.setFillColorRGB(*pen_color)

            # Split text into paragraphs
            paragraphs = re.split(r'\n\s*\n', text)

            y_text = y + height - font_size  # Start from top

            for paragraph in paragraphs:
                words = paragraph.split()
                lines = []
                line = []
                line_width = 0

                for word in words:
                    word_width = canvas.stringWidth(word, 'CustomFont', font_size)
                    if line_width + word_width <= width:
                        line.append(word)
                        line_width += word_width + canvas.stringWidth(' ', 'CustomFont', font_size)
                    else:
                        lines.append(line)
                        line = [word]
                        line_width = word_width

                if line:
                    lines.append(line)

                for i, line in enumerate(lines):
                    if y_text < y:  # If we've reached the bottom of the page
                        canvas.showPage()
                        canvas.setFont('CustomFont', font_size)
                        canvas.setFillColorRGB(*pen_color)
                        y_text = y + height - font_size
                        # Redraw border on new page
                        canvas.setStrokeColorRGB(0.5, 0.5, 0.5)
                        canvas.setLineWidth(1)
                        canvas.rect(x, y, width, height)

                    if len(line) > 1 and i != len(lines) - 1:  # Don't justify the last line of a paragraph
                        total_word_width = sum(canvas.stringWidth(word, 'CustomFont', font_size) for word in line)
                        total_space = width - total_word_width
                        space_width = total_space / (len(line) - 1)
                        max_space_width = canvas.stringWidth('    ', 'CustomFont', font_size)  # Limit to 4 spaces
                        space_width = min(space_width, max_space_width)
                    else:
                        space_width = canvas.stringWidth(' ', 'CustomFont', font_size)

                    x_text = x
                    for word in line:
                        canvas.drawString(x_text, y_text, word)
                        x_text += canvas.stringWidth(word, 'CustomFont', font_size) + space_width

                    y_text -= font_size * 1.5  # Increased line spacing

                # Add extra space between paragraphs
                y_text -= font_size * 0.5

            return canvas

        # Draw text within border
        c = draw_text_in_border(c, text_to_convert, margin, margin, text_width, text_height)

        c.save()
        print(f"PDF saved as {pdf_filename}")
