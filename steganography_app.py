import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

def generate_key_from_password(password):
    salt = b"random_salt"
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
    return kdf.derive(password.encode())

def encrypt_image(image_path, password):
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    key = generate_key_from_password(password)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    padding_length = 16 - len(image_data) % 16
    padded_data = image_data + bytes([padding_length]) * padding_length

    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    encrypted_image_path = image_path.split('.')[0] + "_encrypted.bin"
    with open(encrypted_image_path, "wb") as enc_file:
        enc_file.write(iv + encrypted_data)

    return encrypted_image_path

def decrypt_image(encrypted_image_path, password):
    with open(encrypted_image_path, "rb") as enc_file:
        encrypted_data = enc_file.read()

    iv = encrypted_data[:16]
    encrypted_data = encrypted_data[16:]

    key = generate_key_from_password(password)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

    padding_length = decrypted_data[-1]
    original_data = decrypted_data[:-padding_length]

    decrypted_image_path = encrypted_image_path.replace("_encrypted.bin", "_decrypted.png")
    with open(decrypted_image_path, "wb") as dec_file:
        dec_file.write(original_data)

    return decrypted_image_path

def encrypt_image_ui():
    password = password_entry.get()
    if not password:
        messagebox.showerror("Error", "Please enter a password.")
        return
    
    image_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if not image_path:
        return

    encrypted_image_path = encrypt_image(image_path, password)
    messagebox.showinfo("Success", f"Image encrypted successfully: {encrypted_image_path}")

def decrypt_image_ui():
    password = password_entry.get()
    if not password:
        messagebox.showerror("Error", "Please enter a password.")
        return

    encrypted_image_path = filedialog.askopenfilename(title="Select an Encrypted Image", filetypes=[("Encrypted Files", "*.bin")])
    if not encrypted_image_path:
        return

    try:
        decrypted_image_path = decrypt_image(encrypted_image_path, password)
        messagebox.showinfo("Success", f"Image decrypted successfully: {decrypted_image_path}")
        
        image = Image.open(decrypted_image_path)
        image.show()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during decryption: {str(e)}")

root = tk.Tk()
root.title("Image Encryption and Decryption")
root.geometry("600x500")
root.config(bg="#2E3B4E")

style = ttk.Style()
style.configure("TButton",
                font=("Helvetica", 12),
                padding=10,
                width=20,
                background="#1F2A37",
                foreground="black",
                relief="flat",
                anchor="center")
style.map("TButton",
          background=[('active', '#2A3D54'),
                     ('disabled', '#B0BEC5')])

header_frame = tk.Frame(root, bg="#1F2A37", padx=20, pady=20)
header_frame.pack(fill=tk.X)
header_label = tk.Label(header_frame, text="Encrypt and Decrypt Images", font=("Helvetica", 18, "bold"), bg="#1F2A37", fg="white")
header_label.pack()

password_label = tk.Label(root, text="Enter Password:", font=("Helvetica", 12), bg="#2E3B4E", fg="white")
password_label.pack(pady=10)

password_entry = tk.Entry(root, font=("Helvetica", 12), show="*", width=40, relief="solid", bd=2, highlightbackground="#aaa")
password_entry.pack(pady=10)

button_frame = tk.Frame(root, bg="#2E3B4E")
button_frame.pack(pady=20)

encrypt_button = ttk.Button(button_frame, text="Encrypt Image", command=encrypt_image_ui)
encrypt_button.grid(row=0, column=0, padx=20, pady=10)

decrypt_button = ttk.Button(button_frame, text="Decrypt Image", command=decrypt_image_ui)
decrypt_button.grid(row=0, column=1, padx=20, pady=10)

footer_frame = tk.Frame(root, bg="#2E3B4E", pady=10)
footer_frame.pack(fill=tk.X)
footer_label = tk.Label(footer_frame, text="© 2025 Image Encryption Tool", font=("Helvetica", 10), bg="#2E3B4E", fg="#B0BEC5")
footer_label.pack()

root.mainloop()
