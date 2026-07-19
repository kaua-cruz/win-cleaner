import os
import shutil
from pathlib import Path
from datetime import datetime
from utils import format_bytes, colored

def get_dir_size(path):
    total = 0
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                try:
                    if entry.is_file(follow_symlinks=False):
                        total += entry.stat().st_size
                    elif entry.is_dir(follow_symlinks=False):
                        total += get_dir_size(entry.path)
                except (PermissionError, OSError):
                    continue
    except (PermissionError, OSError):
        pass
    return total

def send_to_trash(path_list):
    success_count = 0
    total_bytes = 0

    has_send2trash = False
    try:
        import send2trash
        has_send2trash = True
    except ImportError:
        pass

    if has_send2trash:
        for path in path_list:
            try:
                if os.path.exists(path):
                    if os.path.isfile(path):
                        total_bytes += os.path.getsize(path)
                    elif os.path.isdir(path):
                        total_bytes += get_dir_size(path)
                    send2trash.send2trash(path)
                    success_count += 1
            except Exception as e:
                print(f"    Erro ao enviar '{path}' para lixeira: {e}")
    else:
        desktop = Path.home() / 'Desktop'
        fallback_dir = desktop / 'Lixeira_win-cleaner'
        fallback_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        batch_dir = fallback_dir / f'deletados_{timestamp}'
        batch_dir.mkdir(exist_ok=True)

        for path in path_list:
            try:
                if os.path.exists(path):
                    if os.path.isfile(path):
                        total_bytes += os.path.getsize(path)
                    elif os.path.isdir(path):
                        total_bytes += get_dir_size(path)
                    dest = batch_dir / os.path.basename(path)
                    shutil.move(path, str(dest))
                    success_count += 1
            except Exception as e:
                print(f"    Erro ao mover '{path}': {e}")

        if success_count > 0:
            print(colored(f"  Arquivos movidos para: {batch_dir}", 'yellow'))

    return success_count, total_bytes
