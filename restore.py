import os
import subprocess
import json
from pathlib import Path
from utils import colored, format_bytes


def get_recycle_bin_contents():
    ps_script = str(Path(__file__).parent / 'read_recycle.ps1')
    if not os.path.exists(ps_script):
        return []

    result = subprocess.run(
        ['powershell', '-ExecutionPolicy', 'Bypass', '-File', ps_script],
        capture_output=True, text=True, timeout=30
    )

    items = []
    for line in result.stdout.split('\n'):
        line = line.strip()
        if not line or line.startswith('Itens:'):
            continue
        parts = line.split('|')
        if len(parts) >= 3:
            recycled_name = parts[0]
            original_path = parts[1].replace('orig:', '', 1)
            display_name = parts[2].replace('name:', '', 1)
            items.append({
                'recycled_name': recycled_name,
                'original_path': original_path,
                'display_name': display_name,
                'full_path': os.path.join(original_path, display_name),
            })

    return items


def restore_item(recycled_name, original_path, display_name):
    ps_script = f'''
    $shell = New-Object -ComObject Shell.Application
    $rb = $shell.NameSpace(10)
    $item = $rb.ParseName("{recycled_name}")
    if ($item -ne $null) {{
        $folder = $shell.NameSpace("{original_path}")
        if ($folder -ne $null) {{
            $folder.MoveHere($item, 16+4+8)
            Write-Host "OK"
        }} else {{
            Write-Host "ERRO: Pasta de destino não encontrada"
        }}
    }} else {{
        Write-Host "ERRO: Item não encontrado na lixeira"
    }}
    '''

    result = subprocess.run(
        ['powershell', '-Command', ps_script],
        capture_output=True, text=True, timeout=30
    )
    return result.stdout.strip()


def show_recycle_bin_menu():
    print(colored("\n  LENDO LIXEIRA...\n", 'yellow', bold=True))

    items = get_recycle_bin_contents()

    if not items:
        print(colored("  Nenhum item encontrado na lixeira.", 'dim'))
        return

    print(colored(f"  Itens na lixeira: {len(items)}\n", 'yellow'))

    print(colored(f"  {'Nº':<4s} {'NOME':<35s} {'ORIGEM':<45s}", 'cyan', bold=True))
    print(colored("  " + "-" * 84, 'cyan'))

    targets = {
        'Local', 'Roaming', 'Program Files', 'Program Files (x86)',
        'ProgramData', 'Temp', 'Programs',
    }

    filtered = []
    for item in items:
        parent = os.path.basename(item['original_path'])
        if parent in targets:
            filtered.append(item)

    if not filtered:
        filtered = items

    for i, item in enumerate(filtered[:30], 1):
        name = item['display_name'] if len(item['display_name']) <= 32 else item['display_name'][:29] + '...'
        orig = item['original_path'] if len(item['original_path']) <= 42 else '...' + item['original_path'][-39:]
        print(f"  {i:<4d} {name:<35s} {orig:<45s}")

    if len(filtered) > 30:
        print(colored(f"  ... e mais {len(filtered) - 30} itens", 'dim'))

    print()
    print(colored("  Digite números para RESTAURAR (ex: 1,3,5)", 'dim'))
    print(colored("  [T]udo  |  [Enter] Voltar", 'dim'))
    choice = input("  Escolha: ").strip().upper()

    if choice in ('', '0'):
        return

    if choice == 'T':
        selected = filtered
    else:
        indices = set()
        for part in choice.split(','):
            part = part.strip()
            if part.isdigit():
                num = int(part)
                if 1 <= num <= len(filtered):
                    indices.add(num)
        selected = [filtered[i-1] for i in sorted(indices)]

    if not selected:
        print(colored("  Nenhum item válido.", 'red'))
        return

    success = 0
    errors = 0
    for item in selected:
        result = restore_item(
            item['recycled_name'],
            item['original_path'],
            item['display_name']
        )
        if 'OK' in result:
            success += 1
        else:
            errors += 1

    print(colored(f"\n  {success} item(ns) restaurado(s).", 'green'))
    if errors:
        print(colored(f"  {errors} falha(s).", 'red'))
