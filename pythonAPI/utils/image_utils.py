import tkinter as tk
from tkinter import filedialog

def choose_image_file():
    root = tk.Tk()
    root.withdraw()
    img_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png")]
    )
    return img_path
