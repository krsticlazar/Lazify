# Lazify

Lazify is a lightweight Windows desktop app that converts `PDF`, `DOCX`, and `PPTX` files into Markdown.

## What It Does

- Accepts `PDF`, `DOCX`, and `PPTX` files
- Lets you drag and drop files or add them manually
- Converts files in the background
- Automatically saves the Markdown output next to the original file
- Creates safe filenames such as `file.md`, `file (1).md`, and so on when needed

## Download And Install

1. Open the repository on GitHub.
2. Go to the **Releases** page.
3. Download `Lazify-Setup.exe`.
4. Run the installer.
5. Choose the folder where you want Lazify to be installed.
6. Finish the setup wizard.

After installation:

- Lazify is added to the **Start Menu**
- A **Lazify** program folder is created
- You can optionally create a desktop shortcut during setup

## How To Use

1. Open Lazify from the Start Menu or desktop shortcut.
2. Drag files into the app or click **Add Files**.
3. Click **Convert All and Save**.
4. The generated Markdown files are saved automatically in the same folder as the original files.

Example:

- `Report.pdf` becomes `Report.md`
- If `Report.md` already exists, Lazify saves `Report (1).md`

## Supported File Types

- `.pdf`
- `.docx`
- `.pptx`

## Installer Output

The GitHub Release should publish:

- `Lazify-Setup.exe`

This is the file end users should download.

## For Development

Install dependencies:

```bat
python -m pip install -r scripts\requirements.txt
```

Run from source:

```bat
python src\main.py
```

Build the app package and installer:

```bat
scripts\build.bat
```

Build outputs:

- App package: `dist\Lazify\Lazify.exe`
- Installer: `dist\installer\Lazify-Setup.exe`
