import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import shutil
import fnmatch
import logging
import sys
from threading import Thread

try:
    from git import Repo
except ImportError:
    print("Error: GitPython is not installed. Please install it using 'pip install GitPython'")
    sys.exit(1)

logging.basicConfig(filename="app_log.txt", level=logging.DEBUG, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

class GrabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub Repo Scraper")
        self.root.geometry("900x700")
        self.root.minsize(900, 700)

        # Set up dark theme colors
        self.bg_color = "#2E2E2E"
        self.fg_color = "#FFFFFF"
        self.button_bg = "#3C3F41"
        self.button_fg = "#FFFFFF"
        self.entry_bg = "#3C3F41"
        self.entry_fg = "#FFFFFF"
        self.tree_bg = "#1E1E1E"
        self.tree_fg = "#FFFFFF"

        self.root.configure(bg=self.bg_color)

        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TButton', background=self.button_bg, foreground=self.button_fg)
        self.style.configure('TEntry', fieldbackground=self.entry_bg, foreground=self.entry_fg)
        self.style.configure('TCheckbutton', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('Treeview', 
                             background=self.tree_bg, 
                             foreground=self.tree_fg, 
                             fieldbackground=self.tree_bg)
        self.style.map('Treeview', background=[('selected', '#4A6984')])

        # Set grid configuration
        self.root.grid_rowconfigure(5, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # GitHub URL label and entry
        self.label_url = ttk.Label(root, text="GitHub URL(s):")
        self.label_url.grid(row=0, column=0, padx=20, pady=5, sticky="w")
        self.entry_url = ttk.Entry(root, width=70)
        self.entry_url.grid(row=0, column=1, columnspan=2, padx=20, pady=5, sticky="we")
        self.entry_url.bind('<Button-3>', self.show_menu)

        # Target folder label and button
        self.label_folder = ttk.Label(root, text="Target Folder (optional):")
        self.label_folder.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        self.entry_folder = ttk.Entry(root, width=50)
        self.entry_folder.grid(row=1, column=1, padx=20, pady=5, sticky="we")
        self.button_browse = ttk.Button(root, text="Browse", command=self.browse_folder)
        self.button_browse.grid(row=1, column=2, padx=5)

        # File extensions frame
        self.extensions_frame = ttk.Frame(root)
        self.extensions_frame.grid(row=2, column=0, columnspan=3, padx=20, pady=5, sticky="we")

        self.extensions_label = ttk.Label(self.extensions_frame, text="File Extensions:")
        self.extensions_label.grid(row=0, column=0, sticky="w")

        self.extensions_entry = ttk.Entry(self.extensions_frame, width=50)
        self.extensions_entry.grid(row=0, column=1, padx=(5, 0), sticky="we")
        self.extensions_entry.insert(0, "py,js,html,css,java,cpp,c,h,hpp,txt,md,json,xml,yaml,yml,sql,sh,bat,ps1,rb,php,go,rs,ts,jsx,tsx")

        # Fetch files button
        self.button_fetch = ttk.Button(root, text="Fetch Files", command=self.fetch_repo_structure)
        self.button_fetch.grid(row=3, column=1, pady=10)

        # Progress bar
        self.style.configure("TProgressbar", background="#4CAF50", troughcolor=self.bg_color, bordercolor=self.bg_color, lightcolor=self.bg_color, darkcolor=self.bg_color)
        self.progress = ttk.Progressbar(root, orient="horizontal", mode="determinate", style="TProgressbar")
        self.progress.grid(row=4, column=1, padx=20, pady=10, sticky="we")

        # Split view for file structure and selection
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.grid(row=5, column=0, columnspan=3, padx=20, pady=5, sticky="nsew")

        # Left side: Treeview for file structure
        self.tree_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.tree_frame, weight=1)

        self.tree = ttk.Treeview(self.tree_frame, selectmode="extended")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)

        # Right side: Listbox for selected items with Add/Remove buttons
        self.selection_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.selection_frame, weight=1)

        self.selection_label = ttk.Label(self.selection_frame, text="Files to be scraped:")
        self.selection_label.pack(side=tk.TOP, anchor="w", padx=5, pady=5)

        self.selection_listbox = tk.Listbox(self.selection_frame, bg=self.tree_bg, fg=self.tree_fg, selectmode=tk.EXTENDED)
        self.selection_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.selection_scrollbar = ttk.Scrollbar(self.selection_frame, orient="vertical", command=self.selection_listbox.yview)
        self.selection_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.selection_listbox.configure(yscrollcommand=self.selection_scrollbar.set)

        # Buttons for adding and removing files
        self.button_frame = ttk.Frame(self.selection_frame)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        self.add_button = ttk.Button(self.button_frame, text="Add Selected", command=self.add_selected_files)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.remove_button = ttk.Button(self.button_frame, text="Remove Selected", command=self.remove_selected_files)
        self.remove_button.pack(side=tk.RIGHT, padx=5)

        # Start button
        self.button_start = ttk.Button(self.root, text="Start Scraping", state=tk.DISABLED, command=self.start_scraping)
        self.button_start.grid(row=6, column=1, pady=10)

        # Context menu for the treeview
        self.tree_menu = tk.Menu(self.root, tearoff=0)
        self.tree_menu.add_command(label="Add", command=self.add_selected_files)
        self.tree_menu.add_command(label="Remove", command=self.remove_selected_files_from_tree)
        self.tree_menu.add_separator()
        self.tree_menu.add_command(label="Select All", command=self.select_all)
        self.tree_menu.add_command(label="Deselect All", command=self.deselect_all)
        self.tree_menu.add_separator()
        self.tree_menu.add_command(label="Expand All", command=self.expand_all)
        self.tree_menu.add_command(label="Collapse All", command=self.collapse_all)

        self.tree.bind("<Button-3>", self.show_tree_menu)
        
        # Set to store the paths of files to be scraped
        self.files_to_scrape = set()

    def show_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Paste", command=lambda: self.entry_url.event_generate("<<Paste>>"))
        menu.post(event.x_root, event.y_root)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.entry_folder.delete(0, tk.END)
            self.entry_folder.insert(0, folder_selected)

    def fetch_repo_structure(self):
        git_urls = self.entry_url.get().split(',')
        target_folder = self.entry_folder.get() or os.getcwd()
        extensions = self.extensions_entry.get().split(',')

        if not git_urls[0]:
            messagebox.showerror("Input Error", "Please enter at least one GitHub URL.")
            return
        
        if not extensions:
            messagebox.showerror("Input Error", "Please enter at least one file extension.")
            return

        logging.debug(f"Fetching repository: {git_urls}")
        self.button_fetch.config(state=tk.DISABLED)
        self.progress["value"] = 10
        Thread(target=self.clone_and_display_structure, args=(git_urls, target_folder, extensions)).start()

    def clone_and_display_structure(self, git_urls, target_folder, extensions):
        try:
            all_repos = []
            for git_url in git_urls:
                git_url = git_url.strip()
                repo_name = git_url.split('/')[-1].replace('.git', '')
                target_path = os.path.join(target_folder, repo_name)

                logging.debug(f"Cloning repository {git_url} to {target_path}")
                Repo.clone_from(git_url, target_path)
                all_repos.append(target_path)
        
            self.update_progress(30)

            self.tree.delete(*self.tree.get_children())

            for repo_path in all_repos:
                repo_node = self.tree.insert("", "end", text=os.path.basename(repo_path), open=True)
                self.populate_tree(repo_path, repo_node, extensions)

            self.update_progress(60)
            self.root.after(0, lambda: self.button_start.config(state=tk.NORMAL))
            logging.debug("Repositories fetched and displayed successfully.")

        except Exception as e:
            logging.error(f"Error during repository fetch: {e}", exc_info=True)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error fetching repository: {e}"))
        finally:
            self.update_progress(100)
            self.root.after(0, lambda: self.button_fetch.config(state=tk.NORMAL))

    def populate_tree(self, path, parent, extensions):
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    folder = self.tree.insert(parent, "end", text=item, open=False, values=(item_path,))
                    self.populate_tree(item_path, folder, extensions)
                else:
                    if any(item.endswith(f".{ext.strip()}") for ext in extensions):
                        self.tree.insert(parent, "end", text=item, values=(item_path,))
        except Exception as e:
            logging.error(f"Error populating tree: {e}", exc_info=True)

    def add_selected_files(self):
        selected_items = self.tree.selection()
        for item in selected_items:
            item_values = self.tree.item(item)['values']
            if item_values:
                file_path = item_values[0]
                if os.path.isfile(file_path):
                    self.files_to_scrape.add(file_path)
                elif os.path.isdir(file_path):
                    self.add_files_from_folder(file_path)
        self.update_selection_listbox()

    def remove_selected_files(self):
        selected_indices = self.selection_listbox.curselection()
        files_to_remove = [self.selection_listbox.get(i) for i in selected_indices]
        for file in files_to_remove:
            self.files_to_scrape.discard(file)
        self.update_selection_listbox()

    def update_selection_listbox(self):
        self.selection_listbox.delete(0, tk.END)
        for file in sorted(self.files_to_scrape):
            self.selection_listbox.insert(tk.END, file)

    def start_scraping(self):
        if not self.files_to_scrape:
            messagebox.showerror("Selection Error", "No files selected for scraping.")
            return

        target_folder = self.entry_folder.get() or os.getcwd()
        self.button_start.config(state=tk.DISABLED)
        Thread(target=self.scrape_and_cleanup, args=(target_folder, list(self.files_to_scrape))).start()

    def scrape_and_cleanup(self, target_folder, selected_files):
        try:
            output_file = os.path.join(target_folder, "scraped_repos.md")

            with open(output_file, "w", encoding="utf-8") as outfile:
                for file_path in selected_files:
                    outfile.write(f"\n## File: {file_path}\n")
                    outfile.write("```\n")
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as infile:
                        outfile.write(infile.read())
                    outfile.write("\n```\n")

            messagebox.showinfo("Success", f"Repositories scraped successfully into {output_file}!")

            # Delete the cloned repos after processing
            for item in self.tree.get_children():
                repo_path = os.path.join(target_folder, self.tree.item(item)['text'])
                shutil.rmtree(repo_path, onerror=self.handle_remove_error)

            self.tree.delete(*self.tree.get_children())

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.button_start.config(state=tk.NORMAL)

    def handle_remove_error(self, func, path, exc_info):
        import stat
        if not os.access(path, os.W_OK):
            os.chmod(path, stat.S_IWUSR)
            func(path)

    def update_progress(self, value):
        self.progress["value"] = value
        self.root.update_idletasks()

    def show_tree_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
        self.tree_menu.post(event.x_root, event.y_root)

    def select_all(self):
        for item in self.tree.get_children():
            self.tree.selection_add(item)

    def deselect_all(self):
        self.tree.selection_remove(self.tree.selection())

    def expand_all(self):
        for item in self.tree.get_children():
            self.tree.item(item, open=True)
            self.expand_children(item)

    def expand_children(self, parent):
        for child in self.tree.get_children(parent):
            self.tree.item(child, open=True)
            self.expand_children(child)

    def collapse_all(self):
        for item in self.tree.get_children():
            self.tree.item(item, open=False)
            self.collapse_children(item)

    def collapse_children(self, parent):
        for child in self.tree.get_children(parent):
            self.tree.item(child, open=False)
            self.collapse_children(child)

    def remove_selected_files_from_tree(self):
        selected_items = self.tree.selection()
        for item in selected_items:
            item_values = self.tree.item(item)['values']
            if item_values:
                file_path = item_values[0]
                if os.path.isfile(file_path):
                    self.files_to_scrape.discard(file_path)
                elif os.path.isdir(file_path):
                    self.remove_files_from_folder(file_path)
        self.update_selection_listbox()

    def remove_files_from_folder(self, folder_path):
        self.files_to_scrape = {f for f in self.files_to_scrape if not f.startswith(folder_path)}

    def add_files_from_folder(self, folder_path):
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                self.files_to_scrape.add(file_path)

def main():
    try:
        root = tk.Tk()
        app = GrabApp(root)
        root.mainloop()
    except Exception as e:
        logging.error(f"Unhandled exception: {e}", exc_info=True)
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()