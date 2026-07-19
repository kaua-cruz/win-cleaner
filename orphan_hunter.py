import os
import re
import subprocess
import winreg
from pathlib import Path
from utils import format_bytes, colored
from scanner import get_dir_size
from trash import send_to_trash

WINDOWS_SYSTEM_FOLDERS = {
    'windows', 'microsoft', 'microsoft.net', 'microsoft shared',
    'common files', 'internet explorer', 'msbuild',
    'reference assemblies', 'windows defender', 'windows nt',
    'windows sidebar', 'windowsapps', 'winxsxs',
    'package cache', 'modifiablewindowsapps',
    'assembly', 'nuget', 'node_modules',
    'windows kits', 'microsoft sdks', 'microsoft sql server',
    'microsoft edge', 'microsoft edge core',
    'microsoft edge webview', 'microsoft one drive',
    'onedrive', 'common files', 'java',
    'intel', 'intel corporation', 'nvidia corporation',
    'nvidia', 'amd', 'ati', 'realtek',
    'vmware', 'oracle', 'docker', 'git',
    'nodejs', 'npm', 'yarn',
    '7-zip', 'winrar', 'winzip',
    'vlc', 'spotify', 'discord', 'slack', 'teams',
    'steam', 'epic games', 'gog', 'ubisoft',
    'brave', 'firefox', 'mozilla', 'chromium',
    'opera', 'vivaldi',
    'notepad++', 'sublime text',
    'total commander', 'everything', 'autohotkey',
    'putty', 'winscp', 'filezilla',
    'openoffice', 'libreoffice', 'microsoft office',
    'powertoys', 'sysinternals',
    'directx',
}


def get_installed_programs():
    programs = set()

    reg_paths = [
        (winreg.HKEY_LOCAL_MACHINE,
         r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE,
         r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER,
         r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]

    for hive, key_path in reg_paths:
        try:
            key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ)
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    try:
                        display_name, _ = winreg.QueryValueEx(
                            subkey, "DisplayName"
                        )
                        if display_name and display_name.strip():
                            programs.add(display_name.strip())
                    except FileNotFoundError:
                        pass
                    finally:
                        winreg.CloseKey(subkey)
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except FileNotFoundError:
            continue

    try:
        result = subprocess.run(
            ['wmic', 'product', 'get', 'name'],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.split('\n')[1:]:
            name = line.strip()
            if name:
                programs.add(name)
    except Exception:
        pass

    return sorted(programs)


def get_appx_packages():
    packages = set()
    try:
        result = subprocess.run(
            ['powershell', '-Command',
             'Get-AppxPackage | Select-Object -ExpandProperty Name'],
            capture_output=True, text=True, timeout=30
        )
        for line in result.stdout.split('\n'):
            name = line.strip()
            if name:
                packages.add(name.split('.')[0].lower())
    except Exception:
        pass
    return packages


def normalize(name):
    name = name.lower()
    name = re.sub(r'[^a-z0-9]', '', name)
    return name


def is_windows_folder(name):
    name_lower = name.lower().strip()
    for known in WINDOWS_SYSTEM_FOLDERS:
        if known.endswith('*'):
            prefix = known[:-1].rstrip('*').strip()
            if name_lower.startswith(prefix):
                return True
        elif name_lower == known:
            return True
    return False


def is_program_installed(folder_name, installed_names, appx_names):
    fnorm = normalize(folder_name)
    if not fnorm or len(fnorm) < 3:
        return True

    for prog in installed_names:
        pnorm = normalize(prog)
        if fnorm in pnorm or pnorm in fnorm:
            return True

    for pkg in appx_names:
        pnorm = normalize(pkg)
        if fnorm in pnorm or pnorm in fnorm:
            return True

    return False


def scan_directory_for_orphans(path, installed_names, appx_names):
    orphans = []
    if not os.path.exists(path):
        return orphans

    try:
        with os.scandir(path) as entries:
            for entry in entries:
                if not entry.is_dir(follow_symlinks=False):
                    continue

                name = entry.name
                if name.startswith('$') or name.startswith('.'):
                    continue
                if is_windows_folder(name):
                    continue
                if not is_program_installed(name, installed_names, appx_names):
                    size = get_dir_size(entry.path)
                    if size > 0:
                        orphans.append((entry.path, size))

        return sorted(orphans, key=lambda x: x[1], reverse=True)
    except (PermissionError, OSError):
        return orphans


def scan_orphans(progress_callback=None):
    installed = get_installed_programs()
    appx = get_appx_packages()
    home = Path.home()
    system_root = os.environ.get('SystemRoot', 'C:\\Windows')

    scan_targets = [
        os.path.join(system_root, '..', 'ProgramData'),
        os.path.join(system_root, '..', 'Program Files'),
        os.path.join(system_root, '..', 'Program Files (x86)'),
        str(home / 'AppData' / 'Local'),
        str(home / 'AppData' / 'Roaming'),
        str(home / 'AppData' / 'Local' / 'Programs'),
    ]

    all_orphans = []
    total = len(scan_targets)

    for i, target in enumerate(scan_targets):
        if progress_callback:
            progress_callback(i + 1, total, target)
        orphans = scan_directory_for_orphans(
            target, installed, appx
        )
        all_orphans.extend(orphans)

    return sorted(all_orphans, key=lambda x: x[1], reverse=True), installed
