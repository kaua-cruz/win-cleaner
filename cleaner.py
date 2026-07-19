import os
from pathlib import Path
from trash import send_to_trash, get_dir_size
from utils import format_bytes, colored

def get_cleanup_targets():
    targets = []
    home = Path.home()
    system_root = os.environ.get('SystemRoot', 'C:\\Windows')

    targets.append({
        'name': 'Temp do Windows',
        'path': os.path.join(system_root, 'Temp'),
        'category': 'Sistema',
    })

    user_temp = os.environ.get('TEMP', str(home / 'AppData' / 'Local' / 'Temp'))
    targets.append({
        'name': 'Temp do Usuário',
        'path': user_temp,
        'category': 'Sistema',
    })

    targets.append({
        'name': 'Prefetch',
        'path': os.path.join(system_root, 'Prefetch'),
        'category': 'Sistema',
    })

    soft_dist = os.path.join(system_root, 'SoftwareDistribution', 'Download')
    targets.append({
        'name': 'Cache do Windows Update',
        'path': soft_dist,
        'category': 'Sistema',
    })

    chrome_cache = home / 'AppData' / 'Local' / 'Google' / 'Chrome' / 'User Data' / 'Default' / 'Cache'
    targets.append({
        'name': 'Cache do Chrome',
        'path': str(chrome_cache),
        'category': 'Navegadores',
    })

    edge_cache = home / 'AppData' / 'Local' / 'Microsoft' / 'Edge' / 'User Data' / 'Default' / 'Cache'
    targets.append({
        'name': 'Cache do Edge',
        'path': str(edge_cache),
        'category': 'Navegadores',
    })

    chrome_code_cache = home / 'AppData' / 'Local' / 'Google' / 'Chrome' / 'User Data' / 'Default' / 'Code Cache'
    targets.append({
        'name': 'Code Cache do Chrome',
        'path': str(chrome_code_cache),
        'category': 'Navegadores',
    })

    recent = home / 'AppData' / 'Roaming' / 'Microsoft' / 'Windows' / 'Recent'
    targets.append({
        'name': 'Itens Recentes',
        'path': str(recent),
        'category': 'Sistema',
    })

   回收站_info = home / '$Recycle.Bin'
    targets.append({
        'name': 'Lixeira (info)',
        'path': str(回收站_info),
        'category': 'Sistema',
    })

    return targets

def estimate_sizes(targets):
    for target in targets:
        path = target['path']
        if os.path.exists(path):
            try:
                target['size'] = get_dir_size(path)
            except:
                target['size'] = 0
            target['exists'] = True
        else:
            target['size'] = 0
            target['exists'] = False
    return targets

def clean_targets(selected_targets):
    total_freed = 0
    total_items = 0

    for target in selected_targets:
        path = target['path']
        if not os.path.exists(path):
            print(f"  {target['name']}: caminho não encontrado.")
            continue

        items_to_delete = []
        error = False
        try:
            with os.scandir(path) as entries:
                for entry in entries:
                    items_to_delete.append(entry.path)
        except PermissionError:
            print(f"  {target['name']}: sem permissão de acesso. Execute como Administrador.")
            error = True
            continue
        except OSError as e:
            print(f"  {target['name']}: erro ao listar - {e}")
            error = True
            continue

        if error or not items_to_delete:
            continue

        print(f"\n  Limpando '{target['name']}' ({len(items_to_delete)} itens)...")
        success, freed = send_to_trash(items_to_delete)
        total_freed += freed
        total_items += success
        if success > 0:
            print(colored(f"  -> {success} itens enviados para lixeira ({format_bytes(freed)})", 'green'))
        else:
            print(colored(f"  -> Nenhum item limpo.", 'yellow'))

    return total_items, total_freed
