import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time

class ImageToolkitApp:
    def __init__(self, master):
        self.master = master
        master.title("Digital Image Toolkit - Professional Edition")
        master.geometry("1400x800")
        master.configure(bg="#f5f6fa")
        
        # Colors
        self.colors = {
            'primary': '#3498db',
            'secondary': '#2c3e50', 
            'accent': '#e74c3c',
            'success': '#27ae60',
            'warning': '#f39c12',
            'light_bg': '#ecf0f1',
            'dark_bg': '#34495e',
            'sidebar': '#2c3e50',
            'header': '#3498db'
        }

        self.original_image = None
        self.current_image = None
        self.original_path = None
        self.processing = False
        
        self.edit_mode = tk.StringVar(value='enhanced')
        self.history = []
        self.history_index = -1
        
        self.original_tk_image = None
        self.enhanced_tk_image = None
        
        self.setup_gui()

    def setup_gui(self):
        """Setup the main GUI layout"""
        # Main container
        main_container = tk.Frame(self.master, bg=self.colors['light_bg'])
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Configure grid
        main_container.grid_columnconfigure(0, weight=0, minsize=350)  # Sidebar
        main_container.grid_columnconfigure(1, weight=1)  # Image area
        main_container.grid_rowconfigure(0, weight=1)
        
        # Left Sidebar
        self.create_sidebar(main_container)
        
        # Right Image Area
        self.create_image_area(main_container)

    def create_sidebar(self, parent):
        """Create the left sidebar with controls"""
        sidebar = tk.Frame(parent, bg=self.colors['sidebar'], relief='raised', bd=1)
        sidebar.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        
        # Header
        header_frame = tk.Frame(sidebar, bg=self.colors['header'], height=80)
        header_frame.pack(fill='x', pady=(0, 15))
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="Digital Image Toolkit", 
                font=("Arial", 16, "bold"), bg=self.colors['header'], 
                fg='white', pady=20).pack()
        
        tk.Label(header_frame, text="Professional Image Processing Suite", 
                font=("Arial", 10), bg=self.colors['header'], 
                fg='#ecf0f1').pack()
        
        # Content area with scrollbar
        canvas = tk.Canvas(sidebar, bg=self.colors['sidebar'], highlightthickness=0)
        scrollbar = tk.Scrollbar(sidebar, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['sidebar'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=5)
        scrollbar.pack(side="right", fill="y")
        
        # Load content
        self.create_sidebar_content(scrollable_frame)

    def create_sidebar_content(self, parent):
        """Create sidebar content sections"""
        # User Profile
        self.create_profile_section(parent)
        
        # File Operations
        self.create_file_section(parent)
        
        # History Controls
        self.create_history_section(parent)
        
        # Image Processing
        self.create_processing_section(parent)
        
        # Parameters
        self.create_parameters_section(parent)
        
        # Stats
        self.create_stats_section(parent)

    def create_profile_section(self, parent):
        """Create user profile section"""
        profile_frame = tk.Frame(parent, bg=self.colors['sidebar'], pady=15)
        profile_frame.pack(fill='x', padx=10)
        
        # Photo
        photo_frame = tk.Frame(profile_frame, bg='#34495e', width=100, height=100, 
                              relief='sunken', bd=2)
        photo_frame.pack(pady=(0, 10))
        photo_frame.pack_propagate(False)
        
        tk.Label(photo_frame, text="📷\nYour Photo", bg='#34495e', fg='white',
                font=("Arial", 9), justify='center').pack(expand=True)
        
        # Info
        tk.Label(profile_frame, text="Israt Binte ELias", bg=self.colors['sidebar'], 
                fg='white', font=("Arial", 12, "bold")).pack()
        tk.Label(profile_frame, text="#ID-59", bg=self.colors['sidebar'], 
                fg='#bdc3c7', font=("Arial", 10)).pack()

    def create_file_section(self, parent):
        """Create file operations section"""
        section = self.create_section(parent, "📁 File Operations")
        
        # Path display
        path_frame = tk.Frame(section, bg=self.colors['sidebar'])
        path_frame.pack(fill='x', pady=5)
        
        self.path_entry = tk.Entry(path_frame, font=("Arial", 9), state='readonly',
                                  readonlybackground='white', width=30)
        self.path_entry.pack(fill='x', pady=5)
        
        # Buttons
        btn_frame = tk.Frame(section, bg=self.colors['sidebar'])
        btn_frame.pack(fill='x', pady=5)
        
        tk.Button(btn_frame, text="📂 Load Image", command=self.load_image,
                 bg=self.colors['primary'], fg='white', font=("Arial", 10, "bold"),
                 relief='raised', bd=2, padx=15, pady=8, width=12).pack(side='left', padx=(0, 5))
        
        tk.Button(btn_frame, text="💾 Save Result", command=self.save_enhanced_image,
                 bg=self.colors['success'], fg='white', font=("Arial", 10, "bold"),
                 relief='raised', bd=2, padx=15, pady=8, width=12).pack(side='left')

    def create_history_section(self, parent):
        """Create history controls section"""
        section = self.create_section(parent, "🕒 History Controls")
        
        # Edit mode
        mode_frame = tk.Frame(section, bg=self.colors['sidebar'])
        mode_frame.pack(fill='x', pady=5)
        
        tk.Label(mode_frame, text="Edit Mode:", bg=self.colors['sidebar'], 
                fg='white', font=("Arial", 10)).pack(anchor='w')
        
        tk.Radiobutton(mode_frame, text="Enhanced (Stack)", variable=self.edit_mode, 
                      value='enhanced', bg=self.colors['sidebar'], fg='white',
                      selectcolor=self.colors['primary']).pack(anchor='w', pady=2)
        tk.Radiobutton(mode_frame, text="Original (Fresh)", variable=self.edit_mode, 
                      value='original', bg=self.colors['sidebar'], fg='white',
                      selectcolor=self.colors['primary']).pack(anchor='w', pady=2)
        
        # Action buttons
        action_frame = tk.Frame(section, bg=self.colors['sidebar'])
        action_frame.pack(fill='x', pady=10)
        
        tk.Button(action_frame, text="⏪ Undo", command=self.undo_operation,
                 bg='#7f8c8d', fg='white', font=("Arial", 10), width=8,
                 relief='raised', pady=5).pack(side='left', padx=(0, 5))
        
        tk.Button(action_frame, text="⏩ Redo", command=self.redo_operation,
                 bg='#7f8c8d', fg='white', font=("Arial", 10), width=8,
                 relief='raised', pady=5).pack(side='left', padx=(0, 10))
        
        tk.Button(action_frame, text="🔄 Reset", command=self.reset_enhanced_image,
                 bg=self.colors['warning'], fg='white', font=("Arial", 10), width=8,
                 relief='raised', pady=5).pack(side='left')

    def create_processing_section(self, parent):
        """Create image processing buttons section"""
        section = self.create_section(parent, "✨ Image Processing")
        
        # Create two columns
        columns_frame = tk.Frame(section, bg=self.colors['sidebar'])
        columns_frame.pack(fill='x', pady=5)
        
        left_col = tk.Frame(columns_frame, bg=self.colors['sidebar'])
        left_col.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        right_col = tk.Frame(columns_frame, bg=self.colors['sidebar'])
        right_col.pack(side='right', fill='x', expand=True, padx=(5, 0))
        
        # Processing buttons
        buttons_left = [
            ("1. 🎭 Image Negative", self.apply_negative),
            ("2. 🌊 Image Smoothing", self.apply_smoothing),
            ("3. 🔍 Image Sharpening", self.apply_sharpening),
            ("4. 📊 Histogram", self.show_histogram),
        ]
        
        buttons_right = [
            ("5. 📐 Image Resize", self.apply_resize),
            ("6. ⚫ Thresholding", self.apply_thresholding),
            ("7. 🌈 Log & Gamma", self.apply_log_gamma),
            ("8. 🎯 Edge Detection", self.apply_edge_detection),
        ]
        
        for text, command in buttons_left:
            btn = tk.Button(left_col, text=text, command=command, anchor='w',
                          bg='#2980b9', fg='white', font=("Arial", 9),
                          relief='raised', bd=1, padx=10, pady=8)
            btn.pack(fill='x', pady=2)
        
        for text, command in buttons_right:
            btn = tk.Button(right_col, text=text, command=command, anchor='w',
                          bg='#2980b9', fg='white', font=("Arial", 9),
                          relief='raised', bd=1, padx=10, pady=8)
            btn.pack(fill='x', pady=2)

    def create_parameters_section(self, parent):
        """Create parameters section"""
        section = self.create_section(parent, "⚙️ Parameters")
        
        # Parameter entries
        params = [
            ("Smoothing Kernel:", "smoothing_entry", "3"),
            ("Sharpening Factor:", "sharpening_entry", "1.5"),
            ("Resize (WxH):", "resize_entry", "800x600"),
            ("Threshold Value:", "threshold_entry", "128"),
            ("Gamma Value:", "gamma_entry", "2.2"),
        ]
        
        for label, attr_name, default in params:
            frame = tk.Frame(section, bg=self.colors['sidebar'])
            frame.pack(fill='x', pady=3)
            
            tk.Label(frame, text=label, bg=self.colors['sidebar'], 
                    fg='white', font=("Arial", 9)).pack(side='left')
            
            entry = tk.Entry(frame, width=10, font=("Arial", 9))
            entry.insert(0, default)
            entry.pack(side='right', padx=5)
            setattr(self, attr_name, entry)
        
        # Edge detection
        edge_frame = tk.Frame(section, bg=self.colors['sidebar'])
        edge_frame.pack(fill='x', pady=5)
        
        tk.Label(edge_frame, text="Edge Method:", bg=self.colors['sidebar'],
                fg='white', font=("Arial", 9)).pack(side='left')
        
        self.edge_method = tk.StringVar(value="sobel")
        methods = [("Sobel", "sobel"), ("Prewitt", "prewitt"), ("Canny", "canny")]
        
        method_frame = tk.Frame(edge_frame, bg=self.colors['sidebar'])
        method_frame.pack(side='right')
        
        for text, value in methods:
            tk.Radiobutton(method_frame, text=text, variable=self.edge_method,
                          value=value, bg=self.colors['sidebar'], fg='white',
                          font=("Arial", 8), selectcolor=self.colors['primary']).pack(side='left', padx=5)

    def create_stats_section(self, parent):
        """Create statistics section"""
        section = self.create_section(parent, "📊 Quick Stats")
        
        self.stats_text = tk.Text(section, height=8, width=35, bg='#2c3e50', 
                                 fg='white', font=("Arial", 9), relief='flat',
                                 wrap=tk.WORD)
        self.stats_text.pack(fill='x', pady=5)
        self.stats_text.insert('1.0', "No image loaded\n\nLoad an image to see statistics")
        self.stats_text.config(state='disabled')

    def create_section(self, parent, title):
        """Create a section with title"""
        section_frame = tk.Frame(parent, bg=self.colors['sidebar'], relief='groove', bd=1, pady=8)
        section_frame.pack(fill='x', padx=10, pady=8)
        
        tk.Label(section_frame, text=title, font=("Arial", 12, "bold"), 
                bg=self.colors['sidebar'], fg='white').pack(anchor='w', padx=10, pady=(0, 8))
        
        content_frame = tk.Frame(section_frame, bg=self.colors['sidebar'])
        content_frame.pack(fill='x', padx=10)
        
        return content_frame

    def create_image_area(self, parent):
        """Create the right-side image display area"""
        image_area = tk.Frame(parent, bg=self.colors['light_bg'])
        image_area.grid(row=0, column=1, sticky='nsew')
        
        # Configure grid for two equal columns
        image_area.grid_columnconfigure(0, weight=1)
        image_area.grid_columnconfigure(1, weight=1)
        image_area.grid_rowconfigure(0, weight=1)
        
        # Original Image Panel
        self.original_frame = self.create_image_panel(image_area, "Original Image", 0)
        self.original_label = tk.Label(self.original_frame, 
                                      text="📷\nNo image loaded\n\nClick 'Load Image' to begin", 
                                      bg='#34495e', fg='white', font=("Arial", 14),
                                      justify='center')
        self.original_label.pack(fill='both', expand=True)
        
        # Enhanced Image Panel
        self.enhanced_frame = self.create_image_panel(image_area, "Enhanced Image", 1)
        self.enhanced_label = tk.Label(self.enhanced_frame, 
                                      text="✨\nProcessed image\nwill appear here", 
                                      bg='#34495e', fg='white', font=("Arial", 14),
                                      justify='center')
        self.enhanced_label.pack(fill='both', expand=True)

    def create_image_panel(self, parent, title, column):
        """Create individual image panel"""
        panel = tk.Frame(parent, bg=self.colors['dark_bg'], relief='sunken', bd=2)
        panel.grid(row=0, column=column, padx=10, pady=10, sticky='nsew')
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = tk.Label(panel, text=title, bg=self.colors['primary'], 
                              fg='white', font=("Arial", 12, "bold"), pady=8)
        title_label.grid(row=0, column=0, sticky='ew')
        
        # Image container
        img_container = tk.Frame(panel, bg='#2c3e50')
        img_container.grid(row=1, column=0, sticky='nsew', padx=3, pady=3)
        img_container.grid_rowconfigure(0, weight=1)
        img_container.grid_columnconfigure(0, weight=1)
        
        return img_container

    # Core Application Methods
    def load_image(self):
        """Load an image file"""
        if self.processing:
            return
            
        file_path = filedialog.askopenfilename(
            filetypes=(("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff"), 
                      ("All files", "*.*"))
        )
        
        if file_path:
            self.show_loading("Loading image...")
            threading.Thread(target=self.load_image_thread, args=(file_path,), daemon=True).start()

    def load_image_thread(self, file_path):
        """Thread for loading image"""
        try:
            self.processing = True
            image = Image.open(file_path).convert("RGB")
            self.master.after(0, self.finish_load, image, file_path)
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("Error", f"Failed to load image: {e}"))
            self.master.after(0, self.hide_loading)
            self.processing = False

    def finish_load(self, image, file_path):
        """Finish image loading"""
        self.original_image = image
        self.original_path = file_path
        self.reset_history()
        
        self.path_entry.config(state='normal')
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, file_path)
        self.path_entry.config(state='readonly')
        
        self.display_image(self.original_image, self.original_label)
        self.update_stats()
        self.hide_loading()
        self.processing = False

    def display_image(self, img, label):
        """Display image in label"""
        if img is None:
            return

        try:
            # Get container size
            container = label.master
            container.update_idletasks()
            width = container.winfo_width() - 20
            height = container.winfo_height() - 20
            
            if width < 50 or height < 50:
                width, height = 400, 300

            # Resize image
            img_copy = img.copy()
            img_copy.thumbnail((width, height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            tk_img = ImageTk.PhotoImage(img_copy)
            
            # Update label
            label.config(image=tk_img, text="")
            
            # Keep reference
            if label == self.original_label:
                self.original_tk_image = tk_img
            else:
                self.enhanced_tk_image = tk_img
                
        except Exception as e:
            print(f"Display error: {e}")

    def show_loading(self, message):
        """Show loading message"""
        self.enhanced_label.config(text=f"⏳ {message}\n\nPlease wait...", fg='#f39c12')

    def hide_loading(self):
        """Hide loading message"""
        if not self.current_image:
            self.enhanced_label.config(text="✨\nProcessed image\nwill appear here", fg='white')

    def update_stats(self):
        """Update statistics"""
        if self.original_image:
            stats = f"Image Size: {self.original_image.size}\n"
            stats += f"Mode: {self.original_image.mode}\n"
            stats += f"Format: {self.original_image.format or 'Unknown'}\n"
            
            if self.original_image.mode == 'L':
                stats += "\nGrayscale Image"
            else:
                stats += "\nColor Image (RGB)"
            
            self.stats_text.config(state='normal')
            self.stats_text.delete('1.0', tk.END)
            self.stats_text.insert('1.0', stats)
            self.stats_text.config(state='disabled')

    def reset_history(self):
        """Reset history"""
        self.history = []
        self.history_index = -1
        self.current_image = None
        self.enhanced_label.config(image='', text="✨\nProcessed image\nwill appear here")

    def reset_enhanced_image(self):
        """Reset enhanced image"""
        if self.original_image:
            self.current_image = self.original_image.copy()
            self.apply_to_history(self.current_image)

    def save_enhanced_image(self):
        """Save enhanced image"""
        if self.current_image:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
            )
            if file_path:
                try:
                    self.current_image.save(file_path)
                    messagebox.showinfo("Success", "Image saved successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save image: {e}")

    # History Management
    def apply_to_history(self, new_image):
        """Apply to history"""
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
            
        self.history.append(new_image.copy())
        self.history_index = len(self.history) - 1
        self.current_image = new_image
        self.display_image(self.current_image, self.enhanced_label)

    def undo_operation(self):
        """Undo operation"""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_image = self.history[self.history_index].copy()
            self.display_image(self.current_image, self.enhanced_label)

    def redo_operation(self):
        """Redo operation"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_image = self.history[self.history_index].copy()
            self.display_image(self.current_image, self.enhanced_label)

    # Image Processing Operations
    def get_source_image(self):
        """Get source image"""
        if self.edit_mode.get() == 'original':
            return self.original_image.copy() if self.original_image else None
        else:
            return self.current_image if self.current_image else (
                self.original_image.copy() if self.original_image else None)

    def apply_operation(self, operation_func, *args):
        """Apply operation"""
        if self.processing:
            return
            
        source_image = self.get_source_image()
        if source_image is None:
            messagebox.showwarning("Warning", "Please load an image first.")
            return

        self.show_loading("Processing image...")
        threading.Thread(target=self.process_thread, 
                        args=(operation_func, source_image, args), 
                        daemon=True).start()

    def process_thread(self, operation_func, source_image, args):
        """Process in thread"""
        try:
            self.processing = True
            result = operation_func(source_image, *args)
            self.master.after(0, self.finish_processing, result)
        except Exception as e:
            self.master.after(0, lambda: self.processing_error(str(e)))
        finally:
            self.processing = False

    def finish_processing(self, result):
        """Finish processing"""
        self.apply_to_history(result)
        self.hide_loading()

    def processing_error(self, error_msg):
        """Handle processing error"""
        messagebox.showerror("Processing Error", f"Error during processing:\n{error_msg}")
        self.hide_loading()
        self.processing = False

    # Image Processing Functions
    def apply_negative(self):
        def operation(img):
            array = np.array(img)
            return Image.fromarray(255 - array)
        self.apply_operation(operation)

    def apply_smoothing(self):
        def operation(img):
            try:
                kernel_size = max(3, int(self.smoothing_entry.get()))
                if kernel_size % 2 == 0:
                    kernel_size += 1
                return img.filter(ImageFilter.GaussianBlur(kernel_size // 3))
            except ValueError:
                return img.filter(ImageFilter.BLUR)
        self.apply_operation(operation)

    def apply_sharpening(self):
        def operation(img):
            return img.filter(ImageFilter.SHARPEN)
        self.apply_operation(operation)

    def show_histogram(self):
        if self.original_image:
            gray_img = self.original_image.convert('L')
            array = np.array(gray_img)
            
            hist_window = tk.Toplevel(self.master)
            hist_window.title("Image Histogram")
            hist_window.geometry("500x400")
            
            fig, ax = plt.subplots(figsize=(5, 3))
            ax.hist(array.flatten(), bins=256, range=(0, 255), color='skyblue', alpha=0.7)
            ax.set_title("Image Histogram")
            ax.set_xlabel("Pixel Intensity")
            ax.set_ylabel("Frequency")
            ax.grid(True, alpha=0.3)
            
            canvas = FigureCanvasTkAgg(fig, hist_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def apply_resize(self):
        def operation(img):
            try:
                width, height = map(int, self.resize_entry.get().lower().split('x'))
                return img.resize((width, height), Image.Resampling.LANCZOS)
            except ValueError:
                messagebox.showerror("Input Error", "Please enter resize dimensions as 'WxH' (e.g., 800x600)")
                return img
        self.apply_operation(operation)

    def apply_thresholding(self):
        def operation(img):
            try:
                threshold = int(self.threshold_entry.get())
                gray = img.convert('L')
                array = np.array(gray)
                binary = np.where(array >= threshold, 255, 0)
                return Image.fromarray(binary.astype('uint8')).convert('RGB')
            except ValueError:
                messagebox.showerror("Input Error", "Threshold value must be an integer between 0-255")
                return img
        self.apply_operation(operation)

    def apply_log_gamma(self):
        def operation(img):
            try:
                gamma = float(self.gamma_entry.get())
                array = np.array(img, dtype=np.float32) / 255.0
                corrected = np.power(array, 1.0 / gamma)
                result = (corrected * 255).astype(np.uint8)
                return Image.fromarray(result)
            except ValueError:
                messagebox.showerror("Input Error", "Gamma value must be a number")
                return img
        self.apply_operation(operation)

    def apply_edge_detection(self):
        def operation(img):
            method = self.edge_method.get()
            if method == "sobel":
                return img.filter(ImageFilter.FIND_EDGES)
            elif method == "prewitt":
                return img.filter(ImageFilter.EDGE_ENHANCE)
            else:
                return img.filter(ImageFilter.EDGE_ENHANCE_MORE)
        self.apply_operation(operation)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageToolkitApp(root)
    root.mainloop()