import os
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

def scan_top_level(path, progress_callback=None):
    results = {}
    items = []
    try:
        with os.scandir(path) as entries:
            items = [e for e in entries if e.is_dir(follow_symlinks=False)]
    except (PermissionError, OSError) as e:
        print(colored(f"  Erro ao acessar {path}: {e}", 'red'))
        return results

    total = len(items)
    for i, entry in enumerate(items):
        if progress_callback:
            progress_callback(i + 1, total, entry.path)
        size = get_dir_size(entry.path)
        if size > 0:
            results[entry.path] = size

    file_size = 0
    try:
        with os.scandir(path) as entries:
            for e in entries:
                if e.is_file(follow_symlinks=False):
                    file_size += e.stat().st_size
    except (PermissionError, OSError):
        pass

    if file_size > 0:
        label = os.path.join(path, '(arquivos avulsos)')
        results[label] = file_size

    return sorted(results.items(), key=lambda x: x[1], reverse=True)

def scan_user_folders(progress_callback=None):
    home = os.path.expanduser('~')
    folders = [
        ('Desktop', os.path.join(home, 'Desktop')),
        ('Downloads', os.path.join(home, 'Downloads')),
        ('Documents', os.path.join(home, 'Documents')),
        ('Pictures', os.path.join(home, 'Pictures')),
        ('Music', os.path.join(home, 'Music')),
        ('Videos', os.path.join(home, 'Videos')),
        ('AppData\\Local', os.path.join(home, 'AppData', 'Local')),
        ('AppData\\Roaming', os.path.join(home, 'AppData', 'Roaming')),
    ]

    results = {}
    total = len(folders)
    for i, (name, folder) in enumerate(folders):
        if os.path.exists(folder):
            if progress_callback:
                progress_callback(i + 1, total, folder)
            size = get_dir_size(folder)
            if size > 0:
                results[name] = (folder, size)

    sorted_items = sorted(results.items(), key=lambda x: x[1][1], reverse=True)
    return [(label, data[1]) for label, data in sorted_items], {
        label: data[0] for label, data in results.items()
    }

def drill_down(path, progress_callback=None):
    return scan_top_level(path, progress_callback)
