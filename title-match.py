import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import pandas as pd
import Levenshtein
import re

class CSVMatcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Matcher")
        
        self.file1_path = tk.StringVar()
        self.file2_path = tk.StringVar()
        self.col1 = tk.StringVar()
        self.col2 = tk.StringVar()
        self.value_col2 = tk.StringVar()
        self.cutoff_words = tk.StringVar(value="fka, aka")
        self.words_to_strip = tk.StringVar(value="The, And")
        self.chars_to_strip = tk.StringVar(value=",.:")
        
        self.df1 = None
        self.df2 = None
        
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="File 1:").grid(row=0, column=0, sticky=tk.W)
        tk.Entry(self.root, textvariable=self.file1_path).grid(row=0, column=1)
        tk.Button(self.root, text="Browse", command=self.browse_file1).grid(row=0, column=2)
        
        tk.Label(self.root, text="File 2:").grid(row=1, column=0, sticky=tk.W)
        tk.Entry(self.root, textvariable=self.file2_path).grid(row=1, column=1)
        tk.Button(self.root, text="Browse", command=self.browse_file2).grid(row=1, column=2)
        
        tk.Label(self.root, text="Column from File 1:").grid(row=2, column=0, sticky=tk.W)
        self.col1_dropdown = ttk.Combobox(self.root, textvariable=self.col1)
        self.col1_dropdown.grid(row=2, column=1)
        
        tk.Label(self.root, text="Column from File 2:").grid(row=3, column=0, sticky=tk.W)
        self.col2_dropdown = ttk.Combobox(self.root, textvariable=self.col2)
        self.col2_dropdown.grid(row=3, column=1)

        tk.Label(self.root, text="Value from File 2:").grid(row=4, column=0, sticky=tk.W)
        self.value_col2_dropdown = ttk.Combobox(self.root, textvariable=self.value_col2)
        self.value_col2_dropdown.grid(row=4, column=1)
        
        tk.Label(self.root, text="Cut-off Words (comma-separated):").grid(row=5, column=0, sticky=tk.W)
        tk.Entry(self.root, textvariable=self.cutoff_words).grid(row=5, column=1)
        
        tk.Label(self.root, text="Words to Strip (comma-separated):").grid(row=6, column=0, sticky=tk.W)
        tk.Entry(self.root, textvariable=self.words_to_strip).grid(row=6, column=1)
        
        tk.Label(self.root, text="Characters to Strip (without spaces):").grid(row=7, column=0, sticky=tk.W)
        tk.Entry(self.root, textvariable=self.chars_to_strip).grid(row=7, column=1)
        
        tk.Button(self.root, text="Match", command=self.match_files).grid(row=8, column=0, columnspan=3)
    
    def browse_file1(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.file1_path.set(file_path)
            self.load_columns(file_path, self.col1_dropdown)
    
    def browse_file2(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.file2_path.set(file_path)
            self.load_columns(file_path, self.col2_dropdown)
            self.load_columns(file_path, self.value_col2_dropdown)
    
    def load_columns(self, file_path, dropdown):
        try:
            df = pd.read_csv(file_path)
            columns = df.columns.tolist()
            dropdown['values'] = columns
            dropdown.set('')
            
            if dropdown == self.col1_dropdown:
                self.df1 = df
            else:
                self.df2 = df
        except Exception as e:
            messagebox.showerror("Error", f"Error reading file: {e}")
    
    def process_cutoff(self, text, words):
        cut_positions = [text.lower().find(f" {word.strip().lower()}") for word in words.split(',') if f" {word.strip().lower()}" in text.lower()]
        if cut_positions:
            cutoff_index = min(cut_positions)
            text = text[:cutoff_index]
        return text

    def strip_text(self, text, cutoff_words, words, chars):
        # Apply cutoff
        text = self.process_cutoff(text, cutoff_words)
        # Strip words
        for word in words.split(','):
            word = word.strip()
            text = re.sub(r'\b' + re.escape(word) + r'\b', '', text, flags=re.IGNORECASE)
        # Strip characters
        chars = re.escape(chars)
        text = re.sub(r'[' + chars + ']', '', text)
        return text.strip()
    
    def prompt_user_choice(self, value1, options):
        prompt = f"Choose the best match for '{value1}':\n"
        for i, option in enumerate(options):
            prompt += f"{i + 1}. {option}\n"
        choice = simpledialog.askinteger("Choose Match", prompt, minvalue=1, maxvalue=len(options))
        return options[choice - 1] if choice else None
    
    def match_files(self):
        file1_path = self.file1_path.get()
        file2_path = self.file2_path.get()
        col1 = self.col1.get()
        col2 = self.col2.get()
        value_col2 = self.value_col2.get()
        cutoff_words = self.cutoff_words.get()
        words_to_strip = self.words_to_strip.get()
        chars_to_strip = self.chars_to_strip.get()
        
        if not all([file1_path, file2_path, col1, col2, value_col2]):
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        try:
            if self.df1 is None:
                self.df1 = pd.read_csv(file1_path)
            if self.df2 is None:
                self.df2 = pd.read_csv(file2_path)
        except Exception as e:
            messagebox.showerror("Error", f"Error reading files: {e}")
            return
        
        if col1 not in self.df1.columns or col2 not in self.df2.columns or value_col2 not in self.df2.columns:
            messagebox.showerror("Error", "Invalid column names")
            return
        
        df1 = self.df1.copy()
        df2 = self.df2.copy()
        
        df1['cleaned_one'] = df1[col1].apply(lambda x: self.strip_text(str(x), cutoff_words, words_to_strip, chars_to_strip))
        df2['cleaned_two'] = df2[col2].apply(lambda x: self.strip_text(str(x), cutoff_words, words_to_strip, chars_to_strip))
        
        df1['Matched'] = None
        df1['Distance'] = None
        df1[value_col2] = None
        
        for i, value1 in df1['cleaned_one'].items():
            distances = df2['cleaned_two'].apply(lambda x: Levenshtein.distance(value1, x))
            exact_matches = df2[distances == 0]
            close_matches = df2[(distances > 0) & (distances <= 5)]
            
            if len(exact_matches) == 1:
                best_match = exact_matches.iloc[0][col2]
                min_distance = 0
                value_from_file2 = exact_matches.iloc[0][value_col2]
            elif len(exact_matches) > 1:
                options = exact_matches.apply(lambda row: f"{row[col2]}: {row.to_dict()}", axis=1).tolist()
                best_match_str = self.prompt_user_choice(value1, options)
                if best_match_str:
                    best_match_index = options.index(best_match_str)
                    best_match = exact_matches.iloc[best_match_index][col2]
                    min_distance = 0
                    value_from_file2 = exact_matches.iloc[best_match_index][value_col2]
                else:
                    best_match = None
                    min_distance = None
                    value_from_file2 = None
            elif len(close_matches) > 0:
                # Align distances with close_matches
                close_matches['Distance'] = distances[close_matches.index]
                close_matches = close_matches.sort_values(by='Distance').head(25)
                options = close_matches.apply(lambda row: f"{row[col2]}: {row.to_dict()}", axis=1).tolist()
                best_match_str = self.prompt_user_choice(value1, options)
                if best_match_str:
                    best_match_index = options.index(best_match_str)
                    best_match = close_matches.iloc[best_match_index][col2]
                    min_distance = close_matches.iloc[best_match_index]['Distance']
                    value_from_file2 = close_matches.iloc[best_match_index][value_col2]
                else:
                    best_match = None
                    min_distance = None
                    value_from_file2 = None
            else:
                best_match = None
                min_distance = None
                value_from_file2 = None
            
            df1.at[i, 'Matched'] = best_match
            df1.at[i, 'Distance'] = min_distance
            df1.at[i, value_col2] = value_from_file2
        
        df1['Distance'] = df1['Distance'].apply(lambda x: '' if x is None else x)
        df1['Matched'] = df1['Matched'].apply(lambda x: '' if x is None else x)
        df1[value_col2] = df1[value_col2].apply(lambda x: '' if x is None else x)

        output_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if output_file:
            df1.to_csv(output_file, index=False)
            messagebox.showinfo("Success", f"File saved: {output_file}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVMatcherApp(root)
    root.mainloop()
