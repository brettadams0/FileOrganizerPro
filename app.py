import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
import threading
import time


# File categorization based on extensions
def categorize_file(file, custom_categories):
    file_types = {
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
        'Documents': ['.pdf', '.docx', '.txt', '.xlsx', '.pptx'],
        'Videos': ['.mp4', '.avi', '.mov', '.mkv'],
        'Audios': ['.mp3', '.wav', '.flac'],
        'Archives': ['.zip', '.rar', '.tar'],
    }

    # Add custom categories
    for category, extensions in custom_categories.items():
        file_types[category] = extensions

    ext = os.path.splitext(file)[1].lower()

    for category, extensions in file_types.items():
        if ext in extensions:
            return category
    return 'Others'


# Function to organize files
def organize_files(directory, custom_categories, progress_callback, log_callback):
    if not os.path.exists(directory):
        messagebox.showerror("Error", "Directory does not exist.")
        return
    
    # Create folders for each category if they don't exist
    categories = list(custom_categories.keys()) + ['Images', 'Documents', 'Videos', 'Audios', 'Archives', 'Others']
    for category in categories:
        category_folder = os.path.join(directory, category)
        if not os.path.exists(category_folder):
            os.mkdir(category_folder)

    files_moved = 0
    total_files = len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
    
    for index, filename in enumerate(os.listdir(directory)):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            category = categorize_file(filename, custom_categories)
            category_folder = os.path.join(directory, category)
            new_location = os.path.join(category_folder, filename)
            try:
                shutil.move(file_path, new_location)
                files_moved += 1
                log_callback(f"Moved: {filename} to {category}")
            except Exception as e:
                log_callback(f"Error moving file {filename}: {e}")
        
        progress_callback((index + 1) / total_files)

    log_callback(f"Files organized: {files_moved}")


# GUI with tkinter
class FileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Organizer")
        self.root.geometry("600x400")
        self.root.config(bg="#f4f4f4")

        # Set up styling
        self.font = ('Arial', 12)
        self.button_font = ('Arial', 12, 'bold')
        self.color1 = "#4CAF50"  # Green
        self.color2 = "#f4f4f4"  # Light background

        self.selected_directory = ""
        self.custom_categories = {}

        # Setup main UI elements
        self.setup_ui()

    def setup_ui(self):
        # Title Label
        self.title_label = tk.Label(self.root, text="File Organizer", font=('Arial', 20, 'bold'), bg=self.color2, fg=self.color1)
        self.title_label.pack(pady=20)

        # Browse Button to select folder
        self.browse_button = tk.Button(self.root, text="Browse Folder", command=self.browse_folder, font=self.button_font, bg=self.color1, fg="white", relief="solid", width=20)
        self.browse_button.pack(pady=10)

        # Organize Button to start organizing files
        self.organize_button = tk.Button(self.root, text="Organize Files", command=self.organize_files, font=self.button_font, bg=self.color1, fg="white", relief="solid", width=20)
        self.organize_button.pack(pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(self.root, length=400, mode='determinate')
        self.progress.pack(pady=20)

        # Log Output
        self.log_output = tk.Listbox(self.root, width=70, height=10, bg="#333", fg="white", font=self.font)
        self.log_output.pack(pady=10)

        # Settings Button
        self.settings_button = tk.Button(self.root, text="Customize Categories", command=self.customize_categories, font=self.button_font, bg=self.color1, fg="white", relief="solid", width=20)
        self.settings_button.pack(pady=10)

        # Drag and Drop functionality
        self.dnd_label = tk.Label(self.root, text="Drag a folder here to organize", font=self.font, bg=self.color2)
        self.dnd_label.pack(pady=20)
        self.dnd_label.drop_target_register(DND_FILES)
        self.dnd_label.dnd_bind('<<Drop>>', self.on_drop)

    def browse_folder(self):
        self.selected_directory = filedialog.askdirectory()
        if self.selected_directory:
            messagebox.showinfo("Directory Selected", f"Selected folder: {self.selected_directory}")

    def organize_files(self):
        if self.selected_directory:
            threading.Thread(target=organize_files, args=(self.selected_directory, self.custom_categories, self.update_progress, self.update_log)).start()
        else:
            messagebox.showerror("Error", "Please select a directory first.")

    def update_progress(self, progress):
        self.progress['value'] = progress * 100
        self.root.update_idletasks()

    def update_log(self, message):
        self.log_output.insert(tk.END, message)
        self.log_output.yview(tk.END)  # Auto-scroll to the bottom

    def on_drop(self, event):
        self.selected_directory = event.data
        messagebox.showinfo("Directory Dropped", f"Selected folder: {self.selected_directory}")

    def customize_categories(self):
        custom_categories_window = tk.Toplevel(self.root)
        custom_categories_window.title("Custom Categories")
        custom_categories_window.geometry("400x300")

        tk.Label(custom_categories_window, text="Enter custom categories and their extensions (comma separated):", font=self.font).pack(pady=10)

        # User input for categories
        category_input_label = tk.Label(custom_categories_window, text="Category Name (e.g., 'Photos'):", font=self.font)
        category_input_label.pack(pady=5)
        category_name_entry = tk.Entry(custom_categories_window, font=self.font)
        category_name_entry.pack(pady=5)

        extension_input_label = tk.Label(custom_categories_window, text="Extensions (e.g., .jpg, .png):", font=self.font)
        extension_input_label.pack(pady=5)
        extensions_entry = tk.Entry(custom_categories_window, font=self.font)
        extensions_entry.pack(pady=5)

        def save_category():
            category_name = category_name_entry.get()
            extensions = extensions_entry.get().split(',')
            if category_name and extensions:
                self.custom_categories[category_name] = [ext.strip() for ext in extensions]
                messagebox.showinfo("Saved", f"Category '{category_name}' saved!")
                custom_categories_window.destroy()

        save_button = tk.Button(custom_categories_window, text="Save Category", command=save_category, font=self.button_font, bg=self.color1, fg="white")
        save_button.pack(pady=20)

def main():
    root = TkinterDnD.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
