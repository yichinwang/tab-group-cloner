#!/usr/bin/env python3
"""
Simple script to create placeholder icons for the Chrome extension.
Run this to generate basic icons if you don't have design software.
"""

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Installing Pillow...")
    import subprocess
    subprocess.check_call(['pip3', 'install', 'pillow'])
    from PIL import Image, ImageDraw, ImageFont

import os

def create_icon(size):
    """Create a simple gradient icon with text."""
    # Create image with gradient background
    img = Image.new('RGB', (size, size), '#667eea')
    draw = ImageDraw.Draw(img)

    # Draw gradient
    for i in range(size):
        color = (
            int(102 + (118 - 102) * i / size),
            int(126 + (75 - 126) * i / size),
            int(234 + (162 - 234) * i / size)
        )
        draw.line([(0, i), (size, i)], fill=color)

    # Draw simple icon shape (two overlapping rectangles representing browser windows)
    offset = size // 4
    rect_size = size // 2

    # Back rectangle (lighter)
    draw.rectangle(
        [(offset, offset), (offset + rect_size, offset + rect_size)],
        fill='white',
        outline='white',
        width=2
    )

    # Front rectangle (darker)
    draw.rectangle(
        [(offset - 5, offset - 5), (offset + rect_size - 5, offset + rect_size - 5)],
        fill='#4a5fd1',
        outline='white',
        width=2
    )

    # Draw arrow
    arrow_start = (size // 2 + 2, size // 2 - 5)
    arrow_end = (size // 2 + rect_size // 2, size // 2 - 5)
    draw.line([arrow_start, arrow_end], fill='white', width=2)
    # Arrow head
    draw.polygon([
        arrow_end,
        (arrow_end[0] - 4, arrow_end[1] - 3),
        (arrow_end[0] - 4, arrow_end[1] + 3)
    ], fill='white')

    return img

# Create icons directory
icons_dir = os.path.join(os.path.dirname(__file__), 'icons')
os.makedirs(icons_dir, exist_ok=True)

# Create icons in different sizes
sizes = [16, 48, 128]
for size in sizes:
    icon = create_icon(size)
    icon_path = os.path.join(icons_dir, f'icon{size}.png')
    icon.save(icon_path)
    print(f'Created {icon_path}')

print('\nIcons created successfully!')
print('You can now load the extension in Chrome.')
