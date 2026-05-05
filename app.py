import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import csv
from scanner import load_signatures, scan_file, scan_folder

class FileTypeIdentifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Type Identification Tool")
        self.root.geometry("1100x650")
        self.root.configure(bg="#f4f6f8")

        self.db = load_signatures()
        self.results = []

        # Title section
        title_frame = tk.Frame(root, bg="#f4f6f8")
        title_frame.pack(pady=(15, 5))

        tk.Label(
            title_frame,
            text="File Type Identification Tool",
            font=("Segoe UI", 20, "bold"),
            bg="#f4f6f8",
            fg="#1f3b5b"
        ).pack()

        tk.Label(
            title_frame,
            text="Detecting real file types using magic numbers",
            font=("Segoe UI", 11),
            bg="#f4f6f8",
            fg="#4f6475"
        ).pack()

        # Button section
        btn_frame = tk.Frame(root, bg="#f4f6f8")
        btn_frame.pack(pady=10)

        button_style = {
            "font": ("Segoe UI", 10, "bold"),
            "width": 16,
            "padx": 8,
            "pady": 8
        }

        tk.Button(btn_frame, text="Select File", command=self.select_file, **button_style).grid(row=0, column=0, padx=6)
        tk.Button(btn_frame, text="Scan Folder", command=self.select_folder, **button_style).grid(row=0, column=1, padx=6)
        tk.Button(btn_frame, text="Export CSV", command=self.export_csv, **button_style).grid(row=0, column=2, padx=6)
        tk.Button(btn_frame, text="Clear Results", command=self.clear_results, **button_style).grid(row=0, column=3, padx=6)
        tk.Button(btn_frame, text="Supported Types", command=self.show_supported_types, **button_style).grid(row=0, column=4, padx=6)
        tk.Button(btn_frame, text="About", command=self.show_about, **button_style).grid(row=0, column=5, padx=6)

        # Summary section
        summary_frame = tk.Frame(root, bg="#f4f6f8")
        summary_frame.pack(pady=(5, 10))

        self.total_var = tk.StringVar(value="Total Scanned: 0")
        self.suspicious_var = tk.StringVar(value="Suspicious Files: 0")
        self.unknown_var = tk.StringVar(value="Unknown Files: 0")

        self.make_summary_label(summary_frame, self.total_var, 0)
        self.make_summary_label(summary_frame, self.suspicious_var, 1)
        self.make_summary_label(summary_frame, self.unknown_var, 2)

        # Table frame
        table_frame = tk.Frame(root, bg="#f4f6f8")
        table_frame.pack(fill="both", expand=True, padx=15, pady=10)

        columns = ("file", "extension", "detected", "confidence", "note")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=18)

        self.tree.heading("file", text="File")
        self.tree.heading("extension", text="Extension")
        self.tree.heading("detected", text="Detected Type")
        self.tree.heading("confidence", text="Confidence")
        self.tree.heading("note", text="Note / Warning")

        self.tree.column("file", width=280)
        self.tree.column("extension", width=100)
        self.tree.column("detected", width=130)
        self.tree.column("confidence", width=100)
        self.tree.column("note", width=420)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Row highlighting
        self.tree.tag_configure("suspicious", background="#ffe5e5")
        self.tree.tag_configure("unknown", background="#fff4cc")

        # Status bar
        self.status = tk.StringVar()
        self.status.set("Ready.")
        status_bar = tk.Label(
            root,
            textvariable=self.status,
            anchor="w",
            bg="#d9e2ec",
            fg="#102a43",
            font=("Segoe UI", 10),
            padx=10,
            pady=6
        )
        status_bar.pack(fill="x", side="bottom")

    def make_summary_label(self, parent, variable, col):
        frame = tk.Frame(parent, bg="#ffffff", bd=1, relief="solid")
        frame.grid(row=0, column=col, padx=10)
        tk.Label(
            frame,
            textvariable=variable,
            font=("Segoe UI", 11, "bold"),
            bg="#ffffff",
            fg="#1f3b5b",
            width=22,
            pady=10
        ).pack()

    def add_result(self, result):
        self.results.append(result)

        tag = ""
        if result["detected"] == "Unknown":
            tag = "unknown"
        elif result["note"]:
            tag = "suspicious"

        self.tree.insert(
            "",
            tk.END,
            values=(
                result["file"],
                result["extension"],
                result["detected"],
                result["confidence"],
                result["note"]
            ),
            tags=(tag,)
        )

        self.update_summary()

    def update_summary(self):
        total = len(self.results)
        suspicious = sum(1 for r in self.results if r["note"])
        unknown = sum(1 for r in self.results if r["detected"] == "Unknown")

        self.total_var.set(f"Total Scanned: {total}")
        self.suspicious_var.set(f"Suspicious Files: {suspicious}")
        self.unknown_var.set(f"Unknown Files: {unknown}")

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        result = scan_file(file_path, self.db)
        self.add_result(result)
        self.status.set(f"Scanned file: {result['file']}")

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        results = scan_folder(folder_path, self.db)
        for result in results:
            self.add_result(result)

        self.status.set(f"Folder scan completed. Files scanned: {len(results)}")
        messagebox.showinfo("Scan Complete", f"Scanned {len(results)} files.")

    def export_csv(self):
        if not self.results:
            messagebox.showwarning("No Data", "Nothing to export yet.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if not save_path:
            return

        with open(save_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["file", "path", "extension", "detected", "confidence", "note"]
            )
            writer.writeheader()
            writer.writerows(self.results)

        self.status.set("Results exported to CSV successfully.")
        messagebox.showinfo("Export Complete", "Results exported successfully.")

    def clear_results(self):
        self.results = []
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.update_summary()
        self.status.set("Results cleared.")

    def show_supported_types(self):
        supported = []
        for filetype, meta in self.db.items():
            supported.append(f"{filetype} ({meta['ext']})")

        message = "Currently supported file types:\n\n" + "\n".join(supported)
        messagebox.showinfo("Supported File Types", message)

    def show_about(self):
        message = (
            "File Type Identification Tool\n\n"
            "This application identifies the real type of a file by reading\n"
            "its magic number rather than trusting the file extension.\n\n"
            "Main features:\n"
            "- Scan individual files\n"
            "- Scan complete folders\n"
            "- Detect extension mismatches\n"
            "- Export results to CSV\n"
            "- Highlight suspicious and unknown files"
        )
        messagebox.showinfo("About", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileTypeIdentifierApp(root)
    root.mainloop()