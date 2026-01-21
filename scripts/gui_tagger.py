import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import json
import configparser
import google.genai as genai

class CollapsiblePane(ttk.Frame):
    """A collapsible pane widget for tkinter."""
    def __init__(self, parent, text="", **kwargs):
        super().__init__(parent, **kwargs)
        self.text = text
        self.columnconfigure(0, weight=1)
        self._button = ttk.Button(self, text=f"► {self.text}", command=self.toggle)
        self._button.grid(row=0, column=0, sticky="ew")
        self._sub_frame = ttk.Frame(self)

    def toggle(self):
        """Toggles the visibility of the sub-frame."""
        if self._sub_frame.winfo_viewable():
            self._sub_frame.grid_remove()
            self._button.configure(text=f"► {self.text}")
        else:
            self._sub_frame.grid(row=1, column=0, sticky="nsew")
            self._button.configure(text=f"▼ {self.text}")

    @property
    def frame(self):
        return self._sub_frame

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(fill="both", expand=True)

        self.zotero_items = self.load_zotero_items()
        self.tags_df = self.load_tags()
        self.tag_vars = {}
        self.current_item_index = 0

        self.create_widgets()
        self.load_item()

    def load_zotero_items(self):
        try:
            with open('data/zotero_items.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "'data/zotero_items.json' not found. Please run scripts/fetch_abstracts.py first.")
            return []

    def load_tags(self):
        try:
            return pd.read_csv('data/metadata_Dictionary_v2.csv')
        except FileNotFoundError:
            messagebox.showerror("Error", "'data/metadata_Dictionary_v2.csv' not found.")
            return None

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        main_frame.columnconfigure(0, weight=2)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.rowconfigure(3, weight=1)
        left_frame.columnconfigure(0, weight=1)

        title_label = ttk.Label(left_frame, text="Title:")
        title_label.grid(row=0, column=0, sticky="w")
        self.title_text = tk.Text(left_frame, height=2, wrap="word", state="disabled", relief="flat")
        self.title_text.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        abstract_label = ttk.Label(left_frame, text="Abstract:")
        abstract_label.grid(row=2, column=0, sticky="w")
        self.abstract_text = tk.Text(left_frame, wrap="word", state="disabled", relief="flat")
        self.abstract_text.grid(row=3, column=0, sticky="nsew")

        control_frame = ttk.Frame(left_frame)
        control_frame.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        
        self.back_button = ttk.Button(control_frame, text="Back", command=self.go_back)
        self.back_button.pack(side="left", padx=(0, 10))

        self.suggest_button = ttk.Button(control_frame, text="Get Suggestions", command=self.get_suggestions)
        self.suggest_button.pack(side="left", padx=(0, 10))

        self.save_button = ttk.Button(control_frame, text="Save & Next", command=self.save_and_next)
        self.save_button.pack(side="left", padx=(0, 10))

        self.skip_button = ttk.Button(control_frame, text="Skip", command=self.skip)
        self.skip_button.pack(side="left")

        self.progress_label = ttk.Label(control_frame, text="")
        self.progress_label.pack(side="right")

        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)

        canvas = tk.Canvas(right_frame)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if self.tags_df is not None:
            tags_by_category = self.tags_df.groupby('Category')
            for category, tags in tags_by_category:
                pane = CollapsiblePane(scrollable_frame, text=category)
                pane.pack(fill="x", expand=True, pady=2)
                for tag_name in tags['Tag']:
                    var = tk.BooleanVar()
                    cb = ttk.Checkbutton(pane.frame, text=tag_name, variable=var)
                    cb.pack(fill="x", padx=10)
                    self.tag_vars[tag_name] = var

    def load_item(self):
        if not self.zotero_items or self.current_item_index >= len(self.zotero_items):
            self.show_completion_message()
            return

        item = self.zotero_items[self.current_item_index]
        self.title_text.config(state="normal")
        self.abstract_text.config(state="normal")
        self.title_text.delete("1.0", "end")
        self.title_text.insert("1.0", item.get('title', ''))
        self.abstract_text.delete("1.0", "end")
        self.abstract_text.insert("1.0", item.get('abstract', ''))
        self.title_text.config(state="disabled")
        self.abstract_text.config(state="disabled")

        for var in self.tag_vars.values():
            var.set(False)

        # Set checkboxes based on previously saved tags
        if 'assigned_tags' in item:
            for tag_name in item['assigned_tags']:
                if tag_name in self.tag_vars:
                    self.tag_vars[tag_name].set(True)

            
        self.update_progress()

    def update_progress(self):
        total = len(self.zotero_items)
        self.progress_label.config(text=f"Item {self.current_item_index + 1} of {total}")

    def get_suggestions(self):
        if not self.zotero_items or self.current_item_index >= len(self.zotero_items): return
        
        self.progress_label.config(text="Getting suggestions from Gemini...")
        self.master.update_idletasks()

        item = self.zotero_items[self.current_item_index]
        abstract = item.get('abstract', '')
        suggestions = self.get_gemini_suggestions(abstract, self.tags_df)

        if suggestions:
            for tag_name, var in self.tag_vars.items():
                var.set(tag_name in suggestions)
            self.progress_label.config(text="Suggestions loaded.")
        else:
            self.progress_label.config(text="Failed to get suggestions.")
        
        self.master.after(2000, self.update_progress)

    def save_and_next(self):
        self.save_current_tags()
        self.next_item()

    def skip(self):
        self.next_item()

    def next_item(self):
        self.current_item_index += 1
        self.load_item()

    def go_back(self):
        if self.current_item_index > 0:
            self.current_item_index -= 1
            self.load_item()

    def save_current_tags(self):
        if not self.zotero_items or self.current_item_index >= len(self.zotero_items): return
        
        assigned_tags = [tag_name for tag_name, var in self.tag_vars.items() if var.get()]
        if 'reviewed' not in assigned_tags:
            assigned_tags.append('reviewed')
        self.zotero_items[self.current_item_index]['assigned_tags'] = assigned_tags
        
        try:
            with open('data/tagged_items.json', 'w') as f:
                json.dump(self.zotero_items, f, indent=4)
        except IOError as e:
            messagebox.showerror("Error", f"Failed to save tagged items: {e}")

    def get_gemini_suggestions(self, abstract, tags_df):
        config = configparser.ConfigParser()
        config.read('config.ini')
        try:
            gemini_api_key = config['gemini']['api_key']
            if gemini_api_key == 'YOUR_GEMINI_API_KEY':
                messagebox.showwarning("API Key", "Please update 'config.ini' with your Google AI API key.")
                return None
        except (KeyError, FileNotFoundError):
            messagebox.showerror("Error", "Gemini API key not found in 'config.ini'.")
            return None

        client = genai.Client(api_key=gemini_api_key)

        generation_config = {
            "response_mime_type": "application/json",
        }

        model = client.get_generative_model(
            'gemini-1.5-flash',
            generation_config=generation_config,
        )

        tag_definitions = "\n".join([f"Tag: {row['Tag']}, Definition: {row['Definition']}" for index, row in tags_df.iterrows()])
        prompt = f"Classify the following literature abstract by assigning relevant tags from the provided list.\n\nAbstract:\n{abstract}\n\nPossible Tags:\n{tag_definitions}"

        try:
            response = model.generate_content(prompt)
            return json.loads(response.text).get('tags', [])
        except Exception as e:
            messagebox.showerror("Gemini API Error", f"An error occurred: {e}")
            return None
            
    def show_completion_message(self):
        messagebox.showinfo("Done!", "You have tagged all the abstracts.")
        self.save_button.config(state="disabled")
        self.skip_button.config(state="disabled")
        self.suggest_button.config(state="disabled")
        self.back_button.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
