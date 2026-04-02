@echo off
setlocal

cd /d "%~dp0\.."
set "ICON_PATH=%CD%\assets\lazify.ico"
set "ISCC_EXE=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC_EXE%" set "ISCC_EXE=%ProgramFiles%\Inno Setup 6\ISCC.exe"

echo Installing dependencies...
python -m pip install -r scripts\requirements.txt
if errorlevel 1 exit /b 1

echo Cleaning previous build artifacts...
taskkill /IM Lazify.exe /F >nul 2>&1
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

if exist lazify.ico copy /y lazify.ico assets\lazify.ico >nul

echo Building application package...
python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --name Lazify ^
  --paths=src ^
  --specpath build ^
  --icon="%ICON_PATH%" ^
  --add-data "%ICON_PATH%;assets" ^
  --hidden-import=tkinterdnd2 ^
  --exclude-module numpy ^
  --exclude-module pygame ^
  --exclude-module pyreadline3 ^
  --collect-all tkinterdnd2 ^
  src\main.py
if errorlevel 1 exit /b 1

if exist "%ISCC_EXE%" (
  echo Building installer...
  "%ISCC_EXE%" installer\Lazify.iss
  if errorlevel 1 exit /b 1
) else (
  echo Inno Setup was not found. Application package was built, but the installer was skipped.
)

echo Build complete.
echo App package: dist\Lazify\Lazify.exe
if exist dist\installer\Lazify-Setup.exe echo Installer: dist\installer\Lazify-Setup.exe

endlocal
exit /b 0
