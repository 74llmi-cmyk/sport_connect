@echo off
chcp 65001 >nul
echo ========================================
echo   Sport Connect - Démarrage
echo   SFT 2026
echo ========================================
echo.

REM Vérifier que l'environnement virtuel existe
if not exist ".venv" (
    echo [ERREUR] Environnement virtuel non trouvé !
    echo Veuillez d'abord exécuter setup.bat pour installer l'application.
    echo.
    pause
    exit /b 1
)

REM Activer l'environnement virtuel
call .venv\Scripts\activate.bat

echo Démarrage de Sport Connect...
echo.
echo L'application sera accessible sur :
echo   http://127.0.0.1:5000
echo.
echo Appuyez sur Ctrl+C pour arrêter l'application
echo ========================================
echo.

REM Lancer l'application
python app.py
