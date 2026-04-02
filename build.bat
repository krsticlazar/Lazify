@echo off
setlocal

cd /d "%~dp0"

echo Installing dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

echo Cleaning previous build artifacts...
taskkill /IM Lazify.exe /F >nul 2>&1
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist Lazify.spec del /q Lazify.spec

echo Building Lazify.exe...
python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name Lazify ^
  --icon=assets/icon.ico ^
  --hidden-import=tkinterdnd2 ^
  --collect-all markitdown ^
  --collect-all magika ^
  --collect-all tkinterdnd2 ^
  main.py
if errorlevel 1 exit /b 1

echo Build complete. Output available in dist\Lazify.exe
endlocal
exit /b 0
