import os
import platform
import shutil
import string

def enable_ansi():
    if platform.system() == 'Windows':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            pass

def format_bytes(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.1f} MB"
    else:
        return f"{size_bytes / 1024 ** 3:.2f} GB"

def get_disk_usage():
    drives = []
    if platform.system() == 'Windows':
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                try:
                    total, used, free = shutil.disk_usage(drive)
                    drives.append({
                        'drive': drive,
                        'total': total,
                        'used': used,
                        'free': free,
                        'percent': round(used / total * 100, 1) if total > 0 else 0
                    })
                except:
                    pass
    return drives

def colored(text, color='reset', bold=False):
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'dim': '\033[2m',
        'reset': '\033[0m',
    }
    color_code = colors.get(color, colors['reset'])
    bold_code = '\033[1m' if bold else ''
    return f"{bold_code}{color_code}{text}{colors['reset']}"

def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')
