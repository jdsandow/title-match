import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import Levenshtein
import os

class CSVMatcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Matcher")
        
        self.file1_path = tk.StringVar()
        self.file2_path = tk.StringVar()
        self.col1 = tk.StringVar()
        self.col2 = tk.StringVar()
        
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
        
        tk.Button(self.root, text="Match", command=self.match_files).grid(row=4, column=0, columnspan=3)
    
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
    
    def match_files(self):
        file1_path = self.file1_path.get()
        file2_path = self.file2_path.get()
        col1 = self.col1.get()
        col2 = self.col2.get()
        
        if not all([file1_path, file2_path, col1, col2]):
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
        
        if col1 not in self.df1.columns or col2 not in self.df2.columns:
            messagebox.showerror("Error", "Invalid column names")
            return
        
        df1 = self.df1.copy()
        df2 = self.df2.copy()
        
        df1['Matched'] = None
        df1['Distance'] = None
        
        for i, value1 in df1[col1].items():
            distances = df2[col2].apply(lambda x: Levenshtein.distance(value1, x))
            min_distance = distances.min()
            best_match = df2.loc[distances.idxmin(), col2]
            
            df1.at[i, 'Matched'] = best_match
            df1.at[i, 'Distance'] = min_distance
        
        output_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if output_file:
            df1.to_csv(output_file, index=False)
            messagebox.showinfo("Success", f"File saved: {output_file}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVMatcherApp(root)
    root.mainloop()
