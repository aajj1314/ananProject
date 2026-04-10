#!/usr/bin/env python3
"""
Llama.cpp Model Launcher (Python)
"""

import os
import sys
import subprocess
import time
import json
from typing import Optional, List, Dict, Any

# Configuration
LLAMA_CPP_PATH = "/home/anan/llama.cpp"
MODELS_PATH = os.path.join(LLAMA_CPP_PATH, "models")
BUILD_BIN_PATH = os.path.join(LLAMA_CPP_PATH, "build", "bin")

# Threshold to classify as "large model"
LARGE_MODEL_THRESHOLD = 1024 * 1024 * 1024  # 1 GiB


def format_size(size: int) -> str:
    if size >= 1024 ** 3:
        return f"{size / (1024 ** 3):.2f} GB"
    elif size >= 1024 ** 2:
        return f"{size / (1024 ** 2):.2f} MB"
    elif size >= 1024:
        return f"{size / 1024:.2f} KB"
    return f"{size} B"


def scan_large_models() -> List[Dict[str, Any]]:
    models = []
    try:
        for entry in os.listdir(MODELS_PATH):
            entry_path = os.path.join(MODELS_PATH, entry)
            if os.path.isfile(entry_path) and entry.endswith(".gguf"):
                stat_info = os.stat(entry_path)
                if stat_info.st_size > LARGE_MODEL_THRESHOLD:
                    models.append({
                        "name": entry,
                        "path": entry_path,
                        "size": stat_info.st_size
                    })
    except Exception as e:
        print(f"Error scanning models: {e}", file=sys.stderr)
    return sorted(models, key=lambda m: m["name"])


def clear_screen():
    os.system('clear')


def print_menu(models: List[Dict[str, Any]], selected_idx: int,
               run_mode: int, ctx_size: int, ngl: int, port: int):
    print("\033[1;36m══════════════════════════════════════════════════════════════\033[0m")
    print("\033[1;36m          Llama.cpp Model Launcher v1.0 (Python)\033[0m")
    print("\033[1;36m══════════════════════════════════════════════════════════════\033[0m\n")

    print("\033[1;33mAvailable Models:\033[0m\n")

    for i, model in enumerate(models):
        marker = "►" if i == selected_idx else " "
        color = "\033[7m" if i == selected_idx else ""
        reset = "\033[0m" if i == selected_idx else ""
        print(f"  {marker} {color}{i+1}. {model['name']:<45} [{format_size(model['size'])}]{reset}")

    print("\n\033[1;33mCurrent Settings:\033[0m")
    mode_str = {0: "CLI (交互终端)", 1: "Server (API服务)", 2: "Embedding"}.get(run_mode, "Unknown")
    print(f"  运行模式: \033[1;32m{mode_str}\033[0m  Context: \033[1;32m{ctx_size}\033[0m  NGL: \033[1;32m{ngl}\033[0m  Port: \033[1;32m{port}\033[0m")

    print("\n\033[1;33mControls:\033[0m")
    print("  [\033[1;31m↑↓/4/5\033[0m] 选择模型  [\033[1;31m1\033[0m]CLI  [\033[1;31m2\033[0m]Server  [\033[1;31m3\033[0m]Embedding")
    print("  [\033[1;31mC\033[0m]切换Context  [\033[1;31mG\033[0m]切换NGL  [\033[1;31mP\033[0m]设置端口")
    print("  [\033[1;31mENTER\033[0m]启动模型  [\033[1;31mK\033[0m]停止  [\033[1;31mQ\033[0m]退出")


def print_status(process: Optional[subprocess.Popen],
                 current_mode: int, current_model: str, port: int):
    print("\n\033[1;36m────────────────────────────────────────────────────────────────\033[0m")
    if process and process.poll() is None:
        mode_str = {0: "CLI", 1: "Server", 2: "Embedding"}.get(current_mode, "Unknown")
        print(f"\033[1;32m● Running:\033[0m {mode_str} | Model: {current_model} | PID: {process.pid}", end="")
        if current_mode == 1:
            print(f" | Port: {port}", end="")
        print()
    else:
        print("\033[1;33m○ Idle\033[0m - No model running")
    print("\033[1;36m────────────────────────────────────────────────────────────────\033[0m")


def run_cli(model_path: str, ctx_size: int, ngl: int):
    args = [
        os.path.join(BUILD_BIN_PATH, "llama-cli"),
        "-m", model_path,
        "-ngl", str(ngl),
        "-c", str(ctx_size),
        "--color", "on"
    ]
    return subprocess.Popen(args, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)


def run_server(model_path: str, ctx_size: int, ngl: int, port: int):
    args = [
        os.path.join(BUILD_BIN_PATH, "llama-server"),
        "-m", model_path,
        "-ngl", str(ngl),
        "-c", str(ctx_size),
        "--port", str(port)
    ]
    return subprocess.Popen(args, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)


def run_embedding(model_path: str, ngl: int):
    args = [
        os.path.join(BUILD_BIN_PATH, "llama-embedding"),
        "-m", model_path,
        "-ngl", str(ngl)
    ]
    return subprocess.Popen(args, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)


def get_key():
    import termios
    import tty
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            next1 = sys.stdin.read(1)
            next2 = sys.stdin.read(1)
            if next1 == '[':
                if next2 == 'A':
                    return 'UP'
                elif next2 == 'B':
                    return 'DOWN'
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def main():
    running = True
    selected_idx = 0
    run_mode = 0  # 0=CLI,1=Server,2=Embedding
    ctx_size = 4096
    ngl = 999
    port = 8080
    current_process: Optional[subprocess.Popen] = None
    current_mode = 0
    current_model_name = ""

    models = scan_large_models()
    print("Initializing Llama.cpp Launcher (Python)...")
    print(f"Found {len(models)} models")
    time.sleep(0.5)

    while running:
        clear_screen()
        print_menu(models, selected_idx, run_mode, ctx_size, ngl, port)
        print_status(current_process, current_mode, current_model_name, port)
        print("\n\033[1;34m> \033[0m", end="", flush=True)

        if current_process and current_process.poll() is not None:
            current_process = None

        try:
            key = get_key()
        except:
            key = 'q'

        if key in ('UP', 'w', 'W', '4'):
            if selected_idx > 0:
                selected_idx -= 1
        elif key in ('DOWN', 's', 'S', '5'):
            if selected_idx < len(models) - 1:
                selected_idx += 1
        elif key == '1':
            run_mode = 0
        elif key == '2':
            run_mode = 1
        elif key == '3':
            run_mode = 2
        elif key in ('c', 'C'):
            ctx_size = 8192 if ctx_size == 4096 else 4096
        elif key in ('g', 'G'):
            ngl = 0 if ngl == 999 else 999
        elif key in ('p', 'P'):
            clear_screen()
            print_menu(models, selected_idx, run_mode, ctx_size, ngl, port)
            print_status(current_process, current_mode, current_model_name, port)
            try:
                port_input = input("\n\033[1;33mEnter port number: \033[0m").strip()
                if port_input:
                    new_port = int(port_input)
                    if 1 <= new_port <= 65535:
                        port = new_port
            except:
                pass
        elif key in ('k', 'K'):
            if current_process and current_process.poll() is None:
                current_process.terminate()
                try:
                    current_process.wait(timeout=5)
                except:
                    current_process.kill()
                    current_process.wait()
                current_process = None
                current_model_name = ""
        elif key in ('\r', '\n'):
            if models and 0 <= selected_idx < len(models):
                model = models[selected_idx]
                current_model_name = model["name"]
                current_mode = run_mode
                if current_process and current_process.poll() is None:
                    current_process.terminate()
                    try:
                        current_process.wait(timeout=5)
                    except:
                        current_process.kill()
                        current_process.wait()
                if run_mode == 0:
                    current_process = run_cli(model["path"], ctx_size, ngl)
                elif run_mode == 1:
                    current_process = run_server(model["path"], ctx_size, ngl, port)
                elif run_mode == 2:
                    current_process = run_embedding(model["path"], ngl)
        elif key in ('q', 'Q'):
            running = False

    if current_process and current_process.poll() is None:
        current_process.terminate()
        try:
            current_process.wait(timeout=5)
        except:
            current_process.kill()
            current_process.wait()

    clear_screen()
    print("\n\033[1;32mGoodbye!\033[0m\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
