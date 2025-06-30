from PIL import Image, ImageDraw

# Open or create an image
img = Image.new('RGB', (200, 200), color='white')

# Create a drawing object
draw = ImageDraw.Draw(img)

# Draw a rectangle: (x1, y1, x2, y2)
draw.rectangle([50, 50, 150, 150], outline='blue', width=3)

# Draw a line: (x1, y1, x2, y2)
draw.line([0, 0, 200, 200], fill='red', width=2)

# Save or show the image
img.save('output.png')  # You can use shared storage path on Android
# img.show()  # May not work on Android
