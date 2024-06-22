import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

# Function to get the number of color channels based on the image mode
def get_num_channels(mode):
    if mode == 'RGB':
        return 3
    elif mode == 'RGBA':
        return 4
    elif mode == 'L':
        return 1
    else:
        raise ValueError(f"Unsupported image mode: {mode}")

# Function to hide a message in an image
def hide_message(img_path, message):
    img = Image.open(img_path)
    width, height = img.size
    mode = img.mode
    num_channels = get_num_channels(mode)

    msg = message + chr(0)  # Adding null character to mark end of message
    binary_msg = ''.join(format(ord(char), '08b') for char in msg)

    if len(binary_msg) > width * height * num_channels:
        messagebox.showerror("Error", "Message too large to hide in the given image.")
        return

    data = iter(binary_msg)
    modified_pixels = []

    for pixel in img.getdata():
        if len(modified_pixels) < len(binary_msg):
            if mode == 'RGB':
                r, g, b = pixel
                try:
                    new_pixel = (r & ~1 | int(next(data)), g & ~1 | int(next(data)), b & ~1 | int(next(data)))
                except StopIteration:
                    new_pixel = (r, g, b)
            elif mode == 'RGBA':
                r, g, b, a = pixel
                try:
                    new_pixel = (r & ~1 | int(next(data)), g & ~1 | int(next(data)), b & ~1 | int(next(data)), a)
                except StopIteration:
                    new_pixel = (r, g, b, a)
            elif mode == 'L':
                gray = pixel
                try:
                    new_pixel = (gray & ~1 | int(next(data)),)
                except StopIteration:
                    new_pixel = (gray,)
            modified_pixels.append(new_pixel)
        else:
            modified_pixels.append(pixel)

    new_img = Image.new(img.mode, img.size)
    new_img.putdata(modified_pixels)
    output_path = img_path[:-4] + "_output.png"  # Output file path
    new_img.save(output_path)
    messagebox.showinfo("Success", f"Message hidden successfully in {output_path}")

# Function to extract a message from an image
def extract_message(img_path):
    img = Image.open(img_path)
    mode = img.mode
    num_channels = get_num_channels(mode)

    binary_msg = ''

    for pixel in img.getdata():
        if mode == 'RGB':
            r, g, b = pixel
            binary_msg += str(r & 1)
            binary_msg += str(g & 1)
            binary_msg += str(b & 1)
        elif mode == 'RGBA':
            r, g, b, a = pixel
            binary_msg += str(r & 1)
            binary_msg += str(g & 1)
            binary_msg += str(b & 1)
        elif mode == 'L':
            gray = pixel
            binary_msg += str(gray & 1)

    binary_msg = [binary_msg[i:i + 8] for i in range(0, len(binary_msg), 8)]
    extracted_msg = ''.join(chr(int(char, 2)) for char in binary_msg)
    end_index = extracted_msg.find('\x00')
    message = extracted_msg[:end_index] if end_index != -1 else extracted_msg

    return message

# Function to handle hiding message button click
def hide_message_click():
    img_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if img_path:
        message = entry_message.get("1.0", tk.END).strip()
        if message:
            hide_message(img_path, message)
        else:
            messagebox.showerror("Error", "Please enter a message to hide.")

# Function to handle extracting message button click
def extract_message_click():
    img_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if img_path:
        extracted_msg = extract_message(img_path)
        if extracted_msg:
            messagebox.showinfo("Extracted Message", f"Extracted message:\n\n{extracted_msg}")
        else:
            messagebox.showwarning("No Message", "No hidden message found in the selected image.")

# GUI Setup
root = tk.Tk()
root.title("Steganography Tool")

frame_hide = tk.LabelFrame(root, text="Hide Message", padx=10, pady=10)
frame_hide.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

label_message = tk.Label(frame_hide, text="Enter message to hide:")
label_message.pack(pady=(0, 5))

entry_message = tk.Text(frame_hide, height=4)
entry_message.pack(pady=(0, 10), padx=10, fill=tk.BOTH, expand=True)

btn_hide = tk.Button(frame_hide, text="Hide Message", command=hide_message_click)
btn_hide.pack(pady=(0, 10))

frame_extract = tk.LabelFrame(root, text="Extract Message", padx=10, pady=10)
frame_extract.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

btn_extract = tk.Button(frame_extract, text="Extract Message", command=extract_message_click)
btn_extract.pack(pady=(0, 10))

root.mainloop()
