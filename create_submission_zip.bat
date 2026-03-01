@echo off
REM Hackathon Submission ZIP Creator
REM Creates: Kanyaraasi_Track2.zip

echo ========================================
echo Creating Hackathon Submission ZIP
echo ========================================
echo.

REM Get current directory name
for %%I in (.) do set CURRENT_DIR=%%~nxI

echo Current directory: %CURRENT_DIR%
echo.

REM Create ZIP file name
set ZIP_NAME=Kanyaraasi_Track2.zip

echo Creating %ZIP_NAME%...
echo.

REM Remove old ZIP if exists
if exist "%ZIP_NAME%" (
    echo Removing old %ZIP_NAME%...
    del "%ZIP_NAME%"
)

REM Create ZIP using PowerShell (built-in on Windows)
powershell -Command "Compress-Archive -Path * -DestinationPath '%ZIP_NAME%' -Force -CompressionLevel Optimal"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! ZIP file created successfully
    echo ========================================
    echo.
    echo File: %ZIP_NAME%
    echo Location: %CD%
    echo.
    echo Next steps:
    echo 1. Verify the ZIP file contains all project files
    echo 2. Submit via the Google Form link provided
    echo.
) else (
    echo.
    echo ========================================
    echo ERROR: Failed to create ZIP file
    echo ========================================
    echo.
)

pause
