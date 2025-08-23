<h1 align="center"> <span style="color:#1976D2;">Git Push Helper Pro+</span> </h1>

<p align="center">
  <b>A sleek, modern GUI for managing your Git repositories and streamlining your workflow.</b><br>
  <i>Built with Python & PySide6 (Qt6)</i>
</p>

---

## ⚠️ Prerequisites

- **Python 3.8+** (Download: <a href="https://www.python.org/downloads/">python.org/downloads</a>)
- **Git for Windows** (Download: <a href="https://git-scm.com/download/win">git-scm.com/download/win</a>)   
  <span style="color:red;">❗ You MUST install Git for this app to work! It relies on sending commands to the Git executable.</span>

---

## 🛠️ Installation & Usage

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/BO7MEDX/GitPlus.git](https://github.com/BO7MEDX/GitPlus.git)
    cd GitPlus
    ```

2.  **Install requirements:** First, create a file named `requirements.txt` and add the following lines to it:
    ```
    PySide6
    qtawesome
    ```
    Then, install them using this command:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the app:**
    ```bash
    python masterpiece_gui.py 
    ```
    *(Note: The script name has been updated for the new version)*

4.  **Build as an EXE (Windows):**
    ```powershell
    # Install PyInstaller
    pip install pyinstaller
    
    # Build the executable with the icon and necessary settings for PySide6
    python -m PyInstaller --noconsole --onefile --windowed --name GitPlusPro --icon=icon.ico --hidden-import=PySide6.QtSvg masterpiece_gui.py
    ```
    The final executable will be located in the `dist` folder.

---

## ✨ Key Enhancements (Pro+ Version)

- ✨ **Animated & Responsive UI**: Enjoy smooth animations on buttons and a polished fade-in effect on startup.
- 🚀 **Dynamic Loading Indicator**: A visual spinner provides clear feedback that the app is processing your commands.
- ⚙️ **Robust Command Queue**: Safely executes Git commands sequentially, preventing errors and race conditions.
- 🎨 **Modern Dark Theme**: A professional and aesthetically pleasing interface.

---

### 🎯 Core Features

- **Status**: View the current git status of your repository.
- **Init**: Initialize a new git repository.
- **Add & Commit**: Stage all changes and commit with a custom message.
- **Push**: Push your branch to a remote GitHub repository.
- **Pull**: Pull the latest changes from the remote.
- **Branch Management**: Create, switch, and delete branches.
- **Stash**: Stash changes, apply stashes, and view the stash list.
- **Diff**: View file differences between commits or the working directory.
- **Commit History**: See the last 20 commits with authors, dates, and messages.
- **Output Terminal**: A read-only terminal to see the results of all git commands.
- **Status Bar**: Get quick, helpful status messages at the bottom of the window.
- **Settings Persistence**: The app remembers your last used repository path.
- **About Dialog**: Information about the application and author.

---

## 📸 Screenshots

<p align="center">
  <img src="screenshot_masterpiece.gif" alt="Main UI of the Masterpiece version" width="800"/>
</p>

---

## 📦 Download

**Latest Windows EXE:** 👉 [Releases & Download](https://github.com/BO7MEDX/GitPlus/releases) 👈  
*(Note: You will need to create a new release with the updated EXE file.)*

---

## 👤 Author

**BO7MEDX** GitHub: [BO7MEDX](https://github.com/BO7MEDX)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Pull requests and suggestions are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 🐞 Issues

If you encounter any problems or have a feature request, please [open an issue](https://github.com/BO7MEDX/GitPlus/issues) on GitHub.

---

<h3 align="center" style="color:#1976D2;">Happy Coding! 🚀</h3>
