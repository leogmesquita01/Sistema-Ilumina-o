"""
Inicializador do Sistema de Iluminação Pública (Streamlit)
Prefeitura Municipal de Boa Saúde / RN — Secretaria de Obras e Infraestrutura
"""

import sys
import os
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MAIN_FILE = BASE_DIR / "app" / "dashboard" / "main.py"

def main():
    print("=" * 60)
    print("  ILUMINASAÚDE — GESTÃO & MAPA DE POSTES COSERN")
    print("  Prefeitura Municipal de Boa Saúde / RN")
    print("  Secretaria de Infraestrutura")
    print("=" * 60)
    print("\nIniciando interface no Streamlit...")
    print("Pressione CTRL + C para encerrar o aplicativo a qualquer momento.\n")

    # Comando para iniciar o Streamlit
    python_exe = sys.executable
    cmd = [python_exe, "-m", "streamlit", "run", str(MAIN_FILE), "--server.port=8501", "--server.headless=false"]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
