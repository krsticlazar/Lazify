# Lazify

Lazify is a lightweight Windows desktop app that converts `PDF`, `DOCX`, `PPT`, and `PPTX` files into Markdown.

[![Download for Windows](https://img.shields.io/badge/Download-Windows%20Installer-2ea44f?style=for-the-badge&logo=windows)](https://github.com/krsticlazar/Lazify/releases/latest/download/Lazify-Setup.msi)

Download the latest installer directly:

**[Download Lazify for Windows](https://github.com/krsticlazar/Lazify/releases/latest/download/Lazify-Setup.msi)**

Alternative link:

- [View all releases](https://github.com/krsticlazar/Lazify/releases)

## What's New In v1.1

- Added support for converting legacy `.ppt` files to Markdown
- Added a custom save location selector while keeping the source folder as the default output location

## What It Does

- Accepts `PDF`, `DOCX`, `PPT`, and `PPTX` files
- Lets you drag and drop files or add them manually
- Converts files in the background
- Saves Markdown either next to the original files or in a custom folder you choose
- Creates safe filenames such as `file.md`, `file (1).md`, and so on when needed
- Supports legacy `.ppt` files on Windows when Microsoft PowerPoint is installed

## Download And Install

1. Open the repository on GitHub.
2. Go to the **Releases** page.
3. Download `Lazify-Setup.msi`.
4. Run the installer.
5. Choose the folder where you want Lazify to be installed.
6. Finish the setup wizard.

After installation:

- Lazify is added to the **Start Menu**
- A **Lazify** program folder is created

## How To Use

1. Open Lazify from the Start Menu.
2. Drag files into the app or click **Add Files**.
3. Leave the default save location as the source folder, or click **Change Address** to pick another folder.
4. Click **Convert All and Save**.
5. The generated Markdown files are saved automatically to the selected location.

Example:

- `Report.pdf` becomes `Report.md`
- `Slides.ppt` becomes `Slides.md`
- If `Report.md` already exists, Lazify saves `Report (1).md`

## Supported File Types

- `.pdf`
- `.docx`
- `.ppt`
- `.pptx`

## Legacy PPT Support

- `.pptx` works directly inside Lazify
- `.ppt` support requires Microsoft PowerPoint to be installed on the same Windows machine
- If PowerPoint is not available, use `.pptx` files or convert the `.ppt` file to `.pptx` first

## Installer Output

The GitHub Release should publish:

- `Lazify-Setup.msi`

This is the file end users should download.

## Ideas

- Next UI milestone: a full GUI visual redesign
- Version `2.0` target: AI integration features
- For ideas, feedback, or collaboration, contact `7krle7@gmail.com`

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
- Installer: `dist\installer\Lazify-Setup.msi`
