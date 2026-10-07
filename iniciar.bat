@echo off
title IluminaSaude - Mapa de Postes COSERN (Boa Saude RN)
cd /d "%~dp0"
echo ========================================================
echo   ILUMINASAUDE - MAPA & GESTAO DE POSTES COSERN
echo   Secretaria de Obras e Infraestrutura - Boa Saude / RN
echo ========================================================
echo Iniciando o Streamlit...
echo.
.\.venv\Scripts\python.exe run.py
pause
