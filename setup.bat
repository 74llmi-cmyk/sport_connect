@echo off
chcp 65001 >nul
echo ========================================
echo   Sport Connect - Installation
echo   SFT 2026
echo ========================================
echo.

REM Vérifier que Python est installé
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas installé ou n'est pas dans le PATH.
    echo Veuillez installer Python 3.7 ou supérieur depuis https://www.python.org/
    pause
    exit /b 1
)

echo [1/6] Vérification de Python... OK
echo.

REM Créer l'environnement virtuel s'il n'existe pas
if not exist ".venv" (
    echo [2/6] Création de l'environnement virtuel...
    python -m venv .venv
    echo      Environnement virtuel créé avec succès
) else (
    echo [2/6] Environnement virtuel déjà existant
)
echo.

REM Activer l'environnement virtuel et installer les dépendances
echo [3/6] Installation des dépendances Python...
call .venv\Scripts\activate.bat
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERREUR] Échec de l'installation des dépendances
    pause
    exit /b 1
)
echo      Dépendances installées avec succès
echo.

REM Initialiser la base de données
echo [4/6] Initialisation de la base de données...
python migrations\init_db.py
if %errorlevel% neq 0 (
    echo [ERREUR] Échec de l'initialisation de la base de données
    pause
    exit /b 1
)
echo.

echo [5/6] Ajout de la géolocalisation...
python migrations\add_geolocation.py
if %errorlevel% neq 0 (
    echo [ERREUR] Échec de l'ajout de la géolocalisation
    pause
    exit /b 1
)
echo.

echo ========================================
echo [6/6] Installation terminée avec succès !
echo ========================================
echo.
echo Pour démarrer l'application :
echo   1. Double-cliquez sur start.bat
echo      OU
echo   2. Tapez : python app.py
echo.
echo Puis ouvrez votre navigateur sur :
echo   http://127.0.0.1:5000
echo.
echo ========================================
pause
