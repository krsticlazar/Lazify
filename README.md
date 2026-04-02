# Lazify

Lazify is a desktop app for converting common document and file formats into Markdown.

## Features

- Drag and drop or browse files from a native Windows desktop UI
- Convert `PDF`, `DOCX`, `XLSX`, `PPTX`, `HTML`, `CSV`, `JSON`, `XML`, `JPG`, `JPEG`, and `PNG`
- Run conversions in the background so the UI stays responsive
- Save each Markdown result individually or save all converted files at once
- Build a single-file Windows executable with PyInstaller

## Project Structure

```text
Lazify/
├── README.md
├── assets/
│   └── lazify.ico
├── scripts/
│   ├── build.bat
│   └── requirements.txt
└── src/
    ├── main.py
    └── lazify/
        ├── app.py
        ├── converter.py
        ├── file_item.py
        ├── main.py
        ├── resources.py
        └── ui/
```

## Run From Source

```bat
python -m pip install -r scripts\requirements.txt
python src\main.py
```

## Build The EXE

```bat
scripts\build.bat
```

After a successful build, the executable is created here:

```text
dist\Lazify.exe
```

## Notes

- `scripts\build.bat` automatically syncs the root `lazify.ico` into `assets\lazify.ico` before packaging.
- The packaged app uses the same Lazify icon for both the executable and the Tkinter window.
