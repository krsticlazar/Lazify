@echo off
setlocal

cd /d "%~dp0\.."
set "ICON_PATH=%CD%\assets\lazify.ico"
set "WIX_EXE=%USERPROFILE%\.dotnet\tools\wix.exe"

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

if exist "%WIX_EXE%" (
  echo Preparing WiX...
  "%WIX_EXE%" eula accept wix7 >nul 2>&1
  "%WIX_EXE%" extension list -g | findstr /I /C:"WixToolset.UI.wixext" >nul
  if errorlevel 1 (
    "%WIX_EXE%" extension add -g WixToolset.UI.wixext
    if errorlevel 1 exit /b 1
  )

  echo Building MSI installer...
  "%WIX_EXE%" build ^
    -arch x64 ^
    -bindpath AppFiles="%CD%\dist\Lazify" ^
    -ext WixToolset.UI.wixext ^
    -intermediatefolder build\wix ^
    installer\Lazify.wxs ^
    -out dist\installer\Lazify-Setup.msi
  if errorlevel 1 exit /b 1
) else (
  echo WiX was not found. Application package was built, but the MSI installer was skipped.
)

echo Build complete.
echo App package: dist\Lazify\Lazify.exe
if exist dist\installer\Lazify-Setup.msi echo Installer: dist\installer\Lazify-Setup.msi

endlocal
exit /b 0
