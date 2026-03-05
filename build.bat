@echo off
echo ============================================
echo PrettyThermo EXE Builder
echo ============================================
echo.

REM Check PyInstaller
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [!] Installing PyInstaller...
    python -m pip install pyinstaller
)

REM Check matplotlib
python -m pip show matplotlib >nul 2>&1
if errorlevel 1 (
    echo [!] Installing matplotlib...
    python -m pip install matplotlib
)

echo [OK] Dependencies ready
echo.

REM Clean previous builds
echo [1/4] Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
echo [OK] Cleaned
echo.

REM Build ThermoApp
echo [2/4] Building ThermoApp.exe...
python -m PyInstaller --onefile --name "ThermoApp" ^
    --add-data "App\core;core" ^
    --add-data "App\gui;gui" ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.ttk ^
    --hidden-import=tkinter.messagebox ^
    --hidden-import=tkinter.filedialog ^
    --hidden-import=matplotlib ^
    --hidden-import=matplotlib.pyplot ^
    --collect-all matplotlib ^
    --collect-all numpy ^
    --collect-all PIL ^
    --console ^
    App\main.py

if errorlevel 1 (
    echo [!] ThermoApp build failed
    exit /b 1
)
echo [OK] ThermoApp.exe built
echo.

REM Build CatalogEditor
echo [3/4] Building CatalogEditor.exe...
python -m PyInstaller --onefile --name "CatalogEditor" ^
    --add-data "CatalogEditor\catalog.py;." ^
    --add-data "CatalogEditor\catalog_writer.py;." ^
    --add-data "CatalogEditor\component.py;." ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.ttk ^
    --hidden-import=tkinter.messagebox ^
    --hidden-import=tkinter.filedialog ^
    --console ^
    CatalogEditor\catalog_app.py

if errorlevel 1 (
    echo [!] CatalogEditor build failed
    exit /b 1
)
echo [OK] CatalogEditor.exe built
echo.

REM Copy exe files
echo [4/4] Copying EXE files to root folder...
copy /Y "dist\ThermoApp.exe" "."
copy /Y "dist\CatalogEditor.exe" "."

echo.
echo ============================================
echo Build completed successfully!
echo ============================================
echo EXE files location: %CD%
echo   - ThermoApp.exe (with matplotlib)
echo   - CatalogEditor.exe
echo ============================================
echo.

REM Auto cleanup temp files
echo [5/5] Cleaning temp files...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"
echo [OK] Cleaned

pause
