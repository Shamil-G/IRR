#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path


def activate_venv():
    """
    Автоматически активирует виртуальное окружение, если оно существует.
    Работает на Windows и Linux/Mac.
    """
    project_root = Path(__file__).resolve().parent
    venv_path = project_root / "venv"

    if not venv_path.exists():
        print("⚠️  Виртуальное окружение не найдено. Пропускаю активацию.")
        return

    if os.name == "nt":  # Windows
        activate_script = venv_path / "Scripts" / "activate"
    else:  # Linux / Mac
        activate_script = venv_path / "bin" / "activate"

    if activate_script.exists():
        print(f"🔧 Активирую виртуальное окружение: {activate_script}")
        os.environ["VIRTUAL_ENV"] = str(venv_path)
        os.environ["PATH"] = f"{activate_script.parent}:{os.environ['PATH']}"
    else:
        print("⚠️  Скрипт активации не найден.")


def run_uvicorn():
    """
    Запускает FastAPI-приложение.
    """
    print("🚀 Запускаю сервер FastAPI...")

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
    ]

    subprocess.run(cmd)


if __name__ == "__main__":
    print("=== IRR: Intelligent Run & Reload ===")
    activate_venv()
    run_uvicorn()

