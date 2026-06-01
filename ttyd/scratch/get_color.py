import PIL.Image as Image
import collections

def get_dominant_color(image_path):
    img = Image.open(image_path)
    img = img.convert('RGB')
    img = img.resize((100, 100))
    colors = img.getdata()
    most_common = collections.Counter(colors).most_common(10)
    # Filter out white/black if they are just backgrounds
    for color, count in most_common:
        r, g, b = color
        if r > 240 and g > 240 and b > 240: continue # Skip white
        if r < 10 and g < 10 and b < 10: continue # Skip black
        return '#%02x%02x%02x' % (r, g, b)
    return '#%02x%02x%02x' % most_common[0][0]

print(get_dominant_color('frontend/assets/record_logo_v1.png'))
