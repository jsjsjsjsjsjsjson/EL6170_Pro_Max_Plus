from PIL import Image
import numpy as np
import sys
import os

def apply_jarvis_judice_ninke_dithering(image, invert):
    grayscale_image = image.convert("L")
    arr = np.array(grayscale_image, dtype=np.float32)

    if invert:
        arr = 255 - arr

    height, width = arr.shape

    err_diffusion = np.array([
        [0, 0, 0, 7, 5],
        [3, 5, 7, 5, 3],
        [1, 3, 5, 3, 1]
    ]) / 48

    for y in range(height):
        for x in range(width):
            old_pixel = arr[y, x]
            new_pixel = 255 if old_pixel > 128 else 0
            arr[y, x] = new_pixel
            quant_error = old_pixel - new_pixel
            for dy in range(3):
                for dx in range(-2, 3):
                    if 0 <= x + dx < width and 0 <= y + dy < height:
                        arr[y + dy, x + dx] += quant_error * err_diffusion[dy, dx + 2]

    return Image.fromarray(arr.astype(np.uint8))

def resize_image(image, factor):
    new_size = (round(image.width / factor), round(image.height / factor))
    return image.resize(new_size, Image.LANCZOS)

def setup_gerber_file(filename, width, height):
    with open(filename, 'w') as file:
        file.write("%FSLAX24Y24*%\n")
        file.write("%MOIN*%\n")
        file.write("%LPD*%\n")
        file.write(f"G04 {filename} Size: {width/1000:.3f}in x {height/1000:.3f}in*\n")

def draw_pixel_block(file, x, y, width, pixel_size, height):
    adjusted_y = height - y - pixel_size
    file.write("G36*\n")
    file.write(f"X{x/1000:.3f}Y{adjusted_y/1000:.3f}D02*\n")
    file.write(f"X{(x + width)/1000:.3f}Y{adjusted_y/1000:.3f}D01*\n")
    file.write(f"Y{(adjusted_y + pixel_size)/1000:.3f}D01*\n")
    file.write(f"X{x/1000:.3f}D01*\n")
    file.write(f"Y{adjusted_y/1000:.3f}D01*\n")
    file.write("G37*\n")

def finish_gerber_file(filename):
    with open(filename, 'a') as file:
        file.write("M02*\n")

def main(image_path, resize_factor, invert, output_path, pixel_size):
    image = Image.open(image_path)
    resized_image = resize_image(image, float(resize_factor))
    dithered_image = apply_jarvis_judice_ninke_dithering(resized_image, bool(int(invert)))
    width, height = dithered_image.size
    setup_gerber_file(output_path, width, height)
    pixels = np.array(dithered_image)
    with open(output_path, 'a') as file:
        for y in range(0, pixels.shape[0], pixel_size):
            x = 0
            while x < pixels.shape[1]:
                if pixels[y, x] == 0:
                    start_x = x
                    while x < pixels.shape[1] and pixels[y, x] == 0:
                        x += pixel_size
                    draw_pixel_block(file, start_x, y, x - start_x, pixel_size, height)
                x += pixel_size
    finish_gerber_file(output_path)

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python3 gerberBitmapCreater.py <input_image> <resize_factor> <invert> <output_gerber> <pixel_size_mil>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]))
