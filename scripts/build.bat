@echo off
setlocal

cd /d "%~dp0\.."
set "ICON_PATH=%CD%\assets\lazify.ico"

echo Installing dependencies...
python -m pip install -r scripts\requirements.txt
if errorlevel 1 exit /b 1

echo Cleaning previous build artifacts...
taskkill /IM Lazify.exe /F >nul 2>&1
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

if exist lazify.ico copy /y lazify.ico assets\lazify.ico >nul

echo Building Lazify.exe...
python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name Lazify ^
  --paths=src ^
  --specpath build ^
  --icon="%ICON_PATH%" ^
  --add-data "%ICON_PATH%;assets" ^
  --hidden-import=tkinterdnd2 ^
  --collect-all markitdown ^
  --collect-all magika ^
  --collect-all tkinterdnd2 ^
  src\main.py
if errorlevel 1 exit /b 1

echo Build complete. Output available in dist\Lazify.exe
endlocal
exit /b 0
