import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np

# Utility Functions 

def text_to_binary(text):
    return ''.join(format(ord(char), '08b') for char in text)

def binary_to_text(binary):
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    return ''.join([chr(int(b, 2)) for b in chars])

def encode_matrix(img_array, text):
    binary_data = text_to_binary(text)
    length = len(binary_data)
    length_bin = format(length, '032b')  # First 32 bits = message length
    full_data = length_bin + binary_data

    encoded_img = img_array.copy()
    h, w, _ = img_array.shape
    data_index = 0

    for row in range(h):
        for col in range(w):
            for channel in range(3):
                if data_index < len(full_data):
                    bit = int(full_data[data_index])
                    encoded_img[row, col, channel] = (encoded_img[row, col, channel] & 0b11111110) | bit
                    data_index += 1
                else:
                    return encoded_img
    return encoded_img

def decode_matrix(img_array):
    h, w, _ = img_array.shape
    binary = ''
    data_index = 0

    # First read 32 bits for message length
    for row in range(h):
        for col in range(w):
            for channel in range(3):
                binary += str(img_array[row, col, channel] & 1)
                data_index += 1
                if data_index == 32:
                    break
            if data_index == 32:
                break
        if data_index == 32:
            break

    message_length = int(binary, 2)

    # Now read the actual message bits
    binary = ''
    count = 0
    total_bits = 32 + message_length
    data_index = 0  # reset

    for row in range(h):
        for col in range(w):
            for channel in range(3):
                if data_index >= 32:
                    binary += str(img_array[row, col, channel] & 1)
                    count += 1
                    if count == message_length:
                        return binary_to_text(binary)
                data_index += 1

def text_to_binary(text):
    return ''.join(format(ord(char), '08b') for char in text)

def binary_to_text(binary):
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    return ''.join([chr(int(b, 2)) for b in chars])

# GUI Setup 

root = tk.Tk()
root.title("Image Steganography")
root.geometry("600x500")
root.resizable(False, False)

# Global variables
selected_image = None
img_array = None

# Functions for GUI Buttons

def select_image():
    global selected_image, img_array
    path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
    if not path:
        return

    selected_image = Image.open(path).convert("RGB")
    img_array = np.array(selected_image)

    # Display just the file name
    image_name = path.split("/")[-1]
    file_label.config(text=f"✅ Image selected: {image_name}")

    encode_btn.config(state="normal")
    decode_btn.config(state="normal")

def encode_message():
    global img_array
    if img_array is None:
        messagebox.showerror("Error", "No image selected.")
        return

    text = input_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showerror("Error", "Please enter a message to hide.")
        return

    encoded_array = encode_matrix(img_array, text)
    encoded_image = Image.fromarray(encoded_array.astype('uint8'))
    encoded_image.save("encoded_output.png")
    messagebox.showinfo("Success", "Message encoded and saved as encoded_output.png")
    
def decode_message():
    global img_array
    if img_array is None:
        messagebox.showerror("Error", "No image selected.")
        return

    decoded = decode_matrix(img_array)
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, decoded)

# GUI Layout 

root.configure(bg="#2b2b2b")  # Dark background

font_label = ("Helvetica", 11, "bold")
font_box = ("Consolas", 10)

select_btn = tk.Button(root, text="📂 Select Image", command=select_image, bg="white", fg="black", font=font_label, width=20)
select_btn.pack(pady=15)

file_label = tk.Label(root, text="No image selected", font=("Helvetica", 10), fg="lightgreen", bg="#2b2b2b")
file_label.pack(pady=5)

input_label = tk.Label(root, text="📝 Enter message:", font=font_label, fg="white", bg="#2b2b2b")
input_label.pack(pady=(10, 2))

input_box = tk.Text(root, height=5, width=50, bg="black", fg="white", insertbackground="white", font=font_box)
input_box.config(highlightthickness=0, bd=0)
input_box.pack(pady=(0, 10))

encode_btn = tk.Button(root, text="🔐 Encode", command=encode_message, bg="white", fg="black", font=font_label, width=15)
encode_btn.pack(pady=5)

decode_btn = tk.Button(root, text="🔓 Decode", command=decode_message, bg="white", fg="black", font=font_label, width=15)
decode_btn.pack(pady=5)

output_label = tk.Label(root, text="🧾 Decoded message:", font=font_label, fg="white", bg="#2b2b2b")
output_label.pack(pady=(15, 2))

output_box = tk.Text(root, height=5, width=50, bg="black", fg="white", insertbackground="white", font=font_box)
output_box.config(highlightthickness=0, bd=0)
output_box.pack(pady=(0, 10))

encode_btn.config(state="disabled")
decode_btn.config(state="disabled")

root.mainloop()
