import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import threading
import shutil
import json  # For settings persistence
#coded by Hudulov Hamzat
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)
    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)
    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

class GitPushGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Git Push Helper")
        self.root.geometry("900x700")
        self.root.configure(bg="#2b2b2b")
        self.repo_path = ""
        self.git_path = self.find_git_executable()
        self.all_buttons = []  # Will be filled in setup_ui
        self.status_var = tk.StringVar()
        self.status_var.set("")
        self.setup_ui()
        self.setup_tags()
        self.load_settings()
        # Set minimum window size to keep buttons visible
        self.root.update_idletasks()
        min_width = self.root.winfo_width()
        min_height = self.root.winfo_height()
        self.root.minsize(min_width, min_height)

    def find_git_executable(self):
        """Find Git executable on Windows"""
        # Common Git installation paths on Windows
        common_paths = [
            r"C:\Program Files\Git\bin\git.exe",
            r"C:\Program Files (x86)\Git\bin\git.exe",
            r"C:\Users\{}\AppData\Local\Programs\Git\bin\git.exe".format(os.getenv('USERNAME')),
            "git"  # fallback to system PATH
        ]
        
        # First try to find git using 'where' command
        try:
            result = subprocess.run(['where', 'git'], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                git_path = result.stdout.strip().split('\n')[0]
                return git_path
        except:
            pass
        
        # Try common installation paths
        for path in common_paths:
            if path == "git":
                # Try using shutil to find git in PATH
                git_exe = shutil.which("git")
                if git_exe:
                    return git_exe
            elif os.path.exists(path):
                return path
        
        return "git"  # fallback
    
    def setup_tags(self):
        self.output_text.tag_configure("error", foreground="#ff5555")
        self.output_text.tag_configure("info", foreground="#00ff00")

    def log_output(self, message, error=False):
        tag = "error" if error else "info"
        self.output_text.config(state="normal")
        self.output_text.insert(tk.END, message, tag)
        self.output_text.see(tk.END)
        self.output_text.config(state="disabled")
        if error:
            self.set_status("Error occurred. See output.")
        elif message.strip():
            self.set_status(message.strip().splitlines()[-1][:60])
        self.root.update()

    def enable_buttons(self, enable=True):
        state = tk.NORMAL if enable else tk.DISABLED
        for btn in self.all_buttons:
            btn.config(state=state)

    def setup_ui(self):
        # Menu bar
        menubar = tk.Menu(self.root)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        self.root.config(menu=menubar)
        # Main frame
        main_frame = tk.Frame(self.root, bg="#2b2b2b", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_rowconfigure(6, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = tk.Label(main_frame, text="🚀 Git Push Helper", 
                              font=("Arial", 18, "bold"), 
                              fg="#4CAF50", bg="#2b2b2b")
        title_label.pack(pady=(0, 20))
        
        # Repository selection
        repo_frame = tk.Frame(main_frame, bg="#2b2b2b")
        repo_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(repo_frame, text="Repository Path:", 
                font=("Arial", 10, "bold"), fg="white", bg="#2b2b2b").pack(anchor=tk.W)
        
        path_frame = tk.Frame(repo_frame, bg="#2b2b2b")
        path_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.path_var = tk.StringVar()
        self.path_entry = tk.Entry(path_frame, textvariable=self.path_var, 
                                  font=("Arial", 10), bg="#404040", fg="white",
                                  insertbackground="white")
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(path_frame, text="Browse", 
                              command=self.browse_repository,
                              bg="#555", fg="white", font=("Arial", 9))
        browse_btn.pack(side=tk.RIGHT)
        
        # Remote URL
        remote_frame = tk.Frame(main_frame, bg="#2b2b2b")
        remote_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(remote_frame, text="GitHub Repository URL:", 
                font=("Arial", 10, "bold"), fg="white", bg="#2b2b2b").pack(anchor=tk.W)
        
        self.remote_var = tk.StringVar()
        self.remote_entry = tk.Entry(remote_frame, textvariable=self.remote_var,
                                    font=("Arial", 10), bg="#404040", fg="white",
                                    insertbackground="white")
        self.remote_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Branch selection
        branch_frame = tk.Frame(main_frame, bg="#2b2b2b")
        branch_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(branch_frame, text="Branch:", 
                font=("Arial", 10, "bold"), fg="white", bg="#2b2b2b").pack(anchor=tk.W)
        
        self.branch_var = tk.StringVar(value="main")
        branch_entry = tk.Entry(branch_frame, textvariable=self.branch_var,
                               font=("Arial", 10), bg="#404040", fg="white",
                               insertbackground="white")
        branch_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg="#2b2b2b")
        button_frame.pack(fill=tk.X, pady=(20, 0))
        for i in range(12):
            button_frame.grid_columnconfigure(i, weight=1)
        # Main git buttons
        status_btn = tk.Button(button_frame, text="📊 Status", command=self.check_git_status, bg="#2196F3", fg="white", font=("Arial", 10, "bold"), padx=10, pady=10)
        status_btn.grid(row=0, column=0, sticky="ew", padx=2, pady=3)
        ToolTip(status_btn, "Check the current git status of the repository.")
        init_btn = tk.Button(button_frame, text="🎯 Init", command=self.init_git_repo, bg="#9C27B0", fg="white", font=("Arial", 10, "bold"), padx=10, pady=10)
        init_btn.grid(row=0, column=1, sticky="ew", padx=2, pady=3)
        ToolTip(init_btn, "Initialize a new git repository in the selected folder.")
        commit_btn = tk.Button(button_frame, text="💾 Commit", command=self.add_and_commit, bg="#FF9800", fg="white", font=("Arial", 10, "bold"), padx=10, pady=10)
        commit_btn.grid(row=0, column=2, sticky="ew", padx=2, pady=3)
        ToolTip(commit_btn, "Add all changes and commit with a message.")
        history_btn = tk.Button(button_frame, text="🕑 History", command=self.show_commit_history, bg="#607D8B", fg="white", font=("Arial", 10, "bold"), padx=10, pady=10)
        history_btn.grid(row=0, column=3, sticky="ew", padx=2, pady=3)
        ToolTip(history_btn, "Show the last 10 git commits with notes and dates.")
        push_btn = tk.Button(button_frame, text="🚀 Push", command=self.push_to_github, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), padx=10, pady=10)
        push_btn.grid(row=0, column=4, sticky="ew", padx=2, pady=3)
        ToolTip(push_btn, "Push the current branch to the remote GitHub repository.")
        clear_btn = tk.Button(button_frame, text="🧹 Clear", command=self.clear_output, bg="#333", fg="white", font=("Arial", 10), padx=10, pady=10)
        clear_btn.grid(row=0, column=5, sticky="ew", padx=2, pady=3)
        ToolTip(clear_btn, "Clear the output terminal.")
        # Extra git features
        pull_btn = tk.Button(button_frame, text="⬇️ Pull", command=self.pull_from_remote, bg="#388E3C", fg="white", font=("Arial", 10, "bold"), padx=10, pady=10)
        pull_btn.grid(row=1, column=0, sticky="ew", padx=2, pady=3)
        ToolTip(pull_btn, "Pull latest changes from the remote repository.")
        new_branch_btn = tk.Button(button_frame, text="🌱 New Branch", command=self.create_new_branch, bg="#1976D2", fg="white", font=("Arial", 10, "bold"), padx=10, pady=10)
        new_branch_btn.grid(row=1, column=1, sticky="ew", padx=2, pady=3)
        ToolTip(new_branch_btn, "Create and switch to a new branch.")
        switch_branch_btn = tk.Button(button_frame, text="🔀 Switch Branch", command=self.switch_branch, bg="#455A64", fg="white", font=("Arial", 10, "bold"), padx=10, pady=10)
        switch_branch_btn.grid(row=1, column=2, sticky="ew", padx=2, pady=3)
        ToolTip(switch_branch_btn, "Switch to another branch.")
        del_branch_btn = tk.Button(button_frame, text="❌ Del Branch", command=self.delete_branch, bg="#B71C1C", fg="white", font=("Arial", 10, "bold"), padx=10, pady=10)
        del_branch_btn.grid(row=1, column=3, sticky="ew", padx=2, pady=3)
        ToolTip(del_branch_btn, "Delete a branch.")
        stash_btn = tk.Button(button_frame, text="📥 Stash", command=self.stash_changes, bg="#8D6E63", fg="white", font=("Arial", 10, "bold"), padx=10, pady=10)
        stash_btn.grid(row=1, column=4, sticky="ew", padx=2, pady=3)
        ToolTip(stash_btn, "Stash current changes.")
        pop_stash_btn = tk.Button(button_frame, text="📤 Pop Stash", command=self.apply_stash, bg="#6D4C41", fg="white", font=("Arial", 10, "bold"), padx=10, pady=10)
        pop_stash_btn.grid(row=1, column=5, sticky="ew", padx=2, pady=3)
        ToolTip(pop_stash_btn, "Apply the latest stash.")
        stash_list_btn = tk.Button(button_frame, text="📚 Stash List", command=self.show_stash_list, bg="#5D4037", fg="white", font=("Arial", 10, "bold"), padx=10, pady=10)
        stash_list_btn.grid(row=1, column=6, sticky="ew", padx=2, pady=3)
        ToolTip(stash_list_btn, "Show list of stashes.")
        diff_btn = tk.Button(button_frame, text="📝 Diff", command=self.show_diff, bg="#0288D1", fg="white", font=("Arial", 10, "bold"), padx=10, pady=10)
        diff_btn.grid(row=1, column=7, sticky="ew", padx=2, pady=3)
        ToolTip(diff_btn, "Show file differences (git diff).")
        untracked_btn = tk.Button(button_frame, text="❓ Untracked", command=self.show_untracked_files, bg="#FBC02D", fg="black", font=("Arial", 10, "bold"), padx=10, pady=10)
        untracked_btn.grid(row=1, column=8, sticky="ew", padx=2, pady=3)
        ToolTip(untracked_btn, "Show untracked files.")
        remote_btn = tk.Button(button_frame, text="🌐 Remotes", command=self.show_remotes, bg="#009688", fg="white", font=("Arial", 10, "bold"), padx=10, pady=10)
        remote_btn.grid(row=1, column=9, sticky="ew", padx=2, pady=3)
        ToolTip(remote_btn, "Show remote repositories.")
        self.all_buttons = [status_btn, init_btn, commit_btn, push_btn, history_btn, clear_btn, pull_btn, new_branch_btn, switch_branch_btn, del_branch_btn, stash_btn, pop_stash_btn, stash_list_btn, diff_btn, untracked_btn, remote_btn]
        
        # Output text area
        output_frame = tk.Frame(main_frame, bg="#2b2b2b")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        output_frame.grid_rowconfigure(1, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(output_frame, text="Output:", 
                font=("Arial", 10, "bold"), fg="white", bg="#2b2b2b").pack(anchor=tk.W)
        
        # Text widget with scrollbar
        text_frame = tk.Frame(output_frame, bg="#2b2b2b")
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        self.output_text = tk.Text(text_frame, bg="#1e1e1e", fg="#00ff00",
                                  font=("Consolas", 9), wrap=tk.WORD, state="disabled")
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#222", fg="#fff", font=("Arial", 9))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initial message
        git_status = "✅ Git found" if self.git_path != "git" else "⚠️ Git not found in common locations"
        self.log_output(f"Welcome to Git Push Helper! 🚀\n{git_status}: {self.git_path}\nSelect a repository to get started.\n" + "="*50 + "\n")
    
    def browse_repository(self):
        folder = filedialog.askdirectory(title="Select Git Repository")
        if folder:
            self.path_var.set(folder)
            self.repo_path = folder
            self.log_output(f"Selected repository: {folder}\n")
            # Auto-detect current branch
            try:
                cmd = [self.git_path, 'rev-parse', '--abbrev-ref', 'HEAD']
                result = subprocess.run(cmd, cwd=folder, capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    self.branch_var.set(result.stdout.strip())
            except Exception as e:
                self.log_output(f"❌ Error: {str(e)}\n", error=True)
            # Try to get remote URL if it exists
            try:
                cmd = [self.git_path, 'remote', 'get-url', 'origin']
                result = subprocess.run(cmd, cwd=folder, capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    self.remote_var.set(result.stdout.strip())
                    self.log_output(f"Found remote: {result.stdout.strip()}\n")
            except Exception as e:
                self.log_output(f"❌ Error: {str(e)}\n", error=True)
            self.save_settings()

    def run_git_command(self, command, success_msg=""):
        if not self.repo_path:
            messagebox.showerror("Error", "Please select a repository first!")
            return False
        self.enable_buttons(False)
        try:
            if command[0] == 'git':
                command[0] = self.git_path
            self.log_output(f"Running: {' '.join(command)}\n")
            result = subprocess.run(command, cwd=self.repo_path,
                                   capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                self.log_output(f"✅ {success_msg}\n")
                if result.stdout:
                    self.log_output(f"{result.stdout}\n")
                return True
            else:
                self.log_output(f"❌ Error: {result.stderr}\n", error=True)
                return False
        except Exception as e:
            self.log_output(f"❌ Error: {str(e)}\n", error=True)
            return False
        finally:
            self.enable_buttons(True)

    def init_git_repo(self):
        self.log_output("\n" + "="*30 + " INITIALIZE GIT " + "="*30 + "\n")
        if self.run_git_command(['git', 'init'], "Git repository initialized! 🎉"):
            # Also create a basic .gitignore
            try:
                gitignore_path = os.path.join(self.repo_path, '.gitignore')
                with open(gitignore_path, 'w') as f:
                    f.write("# Python\n__pycache__/\n*.pyc\n*.pyo\n\n# IDE\n.vscode/\n.idea/\n\n# OS\n.DS_Store\nThumbs.db\n")
                self.log_output("Created basic .gitignore file\n")
            except:
                pass
    
    def check_git_status(self):
        self.log_output("\n" + "="*30 + " GIT STATUS " + "="*30 + "\n")
        self.run_git_command(['git', 'status'], "Status checked")
    
    def add_and_commit(self):
        commit_msg = tk.simpledialog.askstring("Commit Message", 
                                              "Enter commit message:",
                                              initialvalue="Update files")
        if not commit_msg:
            return
        
        self.log_output("\n" + "="*30 + " ADD & COMMIT " + "="*30 + "\n")
        
        # Add all files
        if self.run_git_command(['git', 'add', '.'], "Files added to staging"):
            # Commit
            self.run_git_command(['git', 'commit', '-m', commit_msg], 
                               f"Committed with message: '{commit_msg}'")
    
    def push_to_github(self):
        if not self.repo_path:
            messagebox.showerror("Error", "Please select a repository first!")
            return
        
        remote_url = self.remote_var.get().strip()
        branch = self.branch_var.get().strip()
        
        if not remote_url:
            messagebox.showerror("Error", "Please enter a GitHub repository URL!")
            return
        
        def push_async():
            self.log_output("\n" + "="*30 + " PUSHING TO GITHUB " + "="*30 + "\n")
            # Handle existing remote gracefully
            try:
                cmd = [self.git_path, 'remote', 'get-url', 'origin']
                result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    self.run_git_command(['git', 'remote', 'set-url', 'origin', remote_url], "Remote origin updated")
                else:
                    self.run_git_command(['git', 'remote', 'add', 'origin', remote_url], "Remote origin set")
            except Exception as e:
                self.run_git_command(['git', 'remote', 'add', 'origin', remote_url], "Remote origin set")
            self.run_git_command(['git', 'push', '-u', 'origin', branch],
                                f"Successfully pushed to {branch} branch! 🎉")
        
        # Show progress/spinner
        progress = tk.Toplevel(self.root)
        progress.title("Pushing...")
        tk.Label(progress, text="Pushing to GitHub, please wait...", font=("Arial", 12)).pack(padx=20, pady=20)
        progress.geometry("300x80")
        progress.transient(self.root)
        progress.grab_set()
        progress.update()
        def thread_target():
            self.enable_buttons(False)
            push_async()
            progress.destroy()
            self.enable_buttons(True)
        thread = threading.Thread(target=thread_target)
        thread.daemon = True
        thread.start()

    def show_commit_history(self):
        self.log_output("\n" + "="*30 + " COMMIT HISTORY " + "="*30 + "\n")
        try:
            cmd = [self.git_path, 'log', '--pretty=format:%h | %an | %ad | %s', '--date=short', '-n', '10']
            result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                self.log_output("Hash | Author | Date | Message\n", error=False)
                self.log_output("-"*80 + "\n", error=False)
                self.log_output(result.stdout + "\n")
            else:
                self.log_output(f"❌ Error: {result.stderr}\n", error=True)
        except Exception as e:
            self.log_output(f"❌ Error: {str(e)}\n", error=True)

    def clear_output(self):
        self.output_text.config(state="normal")
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state="disabled")
        self.set_status("Output cleared.")

    def set_status(self, message):
        self.status_var.set(message)
        self.root.after(4000, lambda: self.status_var.set(""))

    def save_settings(self):
        data = {
            "repo_path": self.repo_path,
            "branch": self.branch_var.get(),
            "remote": self.remote_var.get()
        }
        try:
            with open("gitpushgui_settings.json", "w") as f:
                json.dump(data, f)
        except:
            pass

    def load_settings(self):
        try:
            with open("gitpushgui_settings.json", "r") as f:
                data = json.load(f)
                self.repo_path = data.get("repo_path", "")
                self.path_var.set(self.repo_path)
                self.branch_var.set(data.get("branch", "main"))
                self.remote_var.set(data.get("remote", ""))
        except:
            pass

    def show_about(self):
        about_text = (
            "Git Push Helper\n\n"
            "A simple, user-friendly GUI to help you manage git repositories and push code to GitHub.\n\n"
            "Features:\n"
            "- Status, Init, Add & Commit, Push\n"
            "- Pull, Branch management, Stash, Diff, Untracked files, Remotes\n"
            "- Commit history with notes and dates\n"
            "- Output terminal, tooltips, and more\n\n"
            "Author: Hamzat Hudulov\n"
            "GitHub: github.com/hudulovhamzat0\n"
            "Email: hamzathudulov@gmail.com\n\n"
            "Made with Python & Tkinter.\n\n"
            "© 2024 Hamzat Hudulov. All rights reserved."
        )
        messagebox.showinfo("About Git Push Helper", about_text)

    def pull_from_remote(self):
        self.log_output("\n" + "="*30 + " GIT PULL " + "="*30 + "\n")
        self.run_git_command(['git', 'pull'], "Pulled latest changes from remote.")

    def create_new_branch(self):
        branch_name = tk.simpledialog.askstring("New Branch", "Enter new branch name:")
        if branch_name:
            self.log_output(f"\n{'='*30} CREATE NEW BRANCH {'='*30}\n")
            if self.run_git_command(['git', 'checkout', '-b', branch_name], f"Created and switched to branch '{branch_name}'"):
                self.branch_var.set(branch_name)
                self.save_settings()

    def switch_branch(self):
        branch_name = tk.simpledialog.askstring("Switch Branch", "Enter branch name to switch to:")
        if branch_name:
            self.log_output(f"\n{'='*30} SWITCH BRANCH {'='*30}\n")
            if self.run_git_command(['git', 'checkout', branch_name], f"Switched to branch '{branch_name}'"):
                self.branch_var.set(branch_name)
                self.save_settings()

    def delete_branch(self):
        branch_name = tk.simpledialog.askstring("Delete Branch", "Enter branch name to delete:")
        if branch_name:
            self.log_output(f"\n{'='*30} DELETE BRANCH {'='*30}\n")
            self.run_git_command(['git', 'branch', '-d', branch_name], f"Deleted branch '{branch_name}'")

    def stash_changes(self):
        self.log_output(f"\n{'='*30} STASH CHANGES {'='*30}\n")
        self.run_git_command(['git', 'stash'], "Stashed current changes.")

    def apply_stash(self):
        self.log_output(f"\n{'='*30} APPLY STASH {'='*30}\n")
        self.run_git_command(['git', 'stash', 'pop'], "Applied latest stash.")

    def show_stash_list(self):
        self.log_output(f"\n{'='*30} STASH LIST {'='*30}\n")
        self.run_git_command(['git', 'stash', 'list'], "Stash list:")

    def show_diff(self):
        self.log_output(f"\n{'='*30} GIT DIFF {'='*30}\n")
        self.run_git_command(['git', 'diff'], "File differences:")

    def show_untracked_files(self):
        self.log_output(f"\n{'='*30} UNTRACKED FILES {'='*30}\n")
        self.run_git_command(['git', 'ls-files', '--others', '--exclude-standard'], "Untracked files:")

    def show_remotes(self):
        self.log_output(f"\n{'='*30} REMOTE REPOSITORIES {'='*30}\n")
        self.run_git_command(['git', 'remote', '-v'], "Remote repositories:")

# Import for commit message dialog
import tkinter.simpledialog

def main():
    root = tk.Tk()
    app = GitPushGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
