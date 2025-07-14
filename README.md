# TempKlean
A simple python Python script to clean temporary files (from `%LOCALAPPDATA%\Temp` and `C:\Windows\Temp`), helping you free up disk space.

---

## Features

- Deletes unnecessary files from:
  - User temp folder: `%LOCALAPPDATA%\Temp`
  - System temp folder: `C:\Windows\Temp`
- Displays how much space was recovered
- Shows a colorful, terminal-based progress bar and summary
- Handles protected or in-use files gracefully

---

## Usage

1. **Requirements**:  
   - Python 3.6+
    
2. **Run the script**:

   ```bash
   python cleanup_temp.py
