import os
import sys
import shutil
from utils import colored, format_bytes, enable_ansi
from orphan_hunter import scan_orphans
from trash import send_to_trash
from restore import show_recycle_bin_menu


def print_header():
    print(colored("=" * 52, 'cyan'))
    print(colored("       WIN-CLEANER — Caçador de Lixo", 'green', bold=True))
    print(colored("       Programas Desinstalados", 'green', bold=True))
    print(colored("=" * 52, 'cyan'))
    print()


def progress_bar(current, total, label):
    bar_len = 28
    if total == 0:
        pct = 100
        filled = bar_len
    else:
        pct = int(current * 100 / total)
        filled = int(bar_len * current // total)
    bar = '#' * filled + '-' * (bar_len - filled)
    short = os.path.basename(label)[:35] if label else ''
    print(f"\r  [{bar}] {pct:>3d}%  {short:<35s}", end='', flush=True)


def make_progress():
    def cb(current, total, label=''):
        progress_bar(current, total, label)
    return cb


def main():
    print_header()
    print(colored("  Varrendo pastas e comparando com programas instalados...\n", 'dim'))

    orphans, installed = scan_orphans(progress_callback=make_progress())
    print("\n")

    if not installed:
        print(colored("  Não foi possível obter lista de programas instalados.", 'red'))
        print(colored("  Tente executar como Administrador.", 'yellow'))
        input("\n  Pressione Enter para sair...")
        return

    print(colored(f"  Programas detectados: {len(installed)}", 'dim'))
    print(colored(f"  Pastas suspeitas encontradas: {len(orphans)}\n", 'yellow'))

    if not orphans:
        print(colored("  Nenhuma pasta órfã encontrada!", 'green'))
        input("\n  Pressione Enter para sair...")
        return

    print(colored(f"  {'Nº':<5s} {'PASTA':<55s} {'TAMANHO':>10s}", 'cyan', bold=True))
    print(colored("  " + "-" * 72, 'cyan'))

    for i, (path, size) in enumerate(orphans[:30], 1):
        name = path if len(path) <= 52 else f"...{path[-49:]}"
        size_str = format_bytes(size)
        cor = 'red' if size > 500*1024**2 else ('yellow' if size > 50*1024**2 else 'green')
        print(f"  {i:<5d} {name:<55s} {colored(size_str.rjust(10), cor)}")

    if len(orphans) > 30:
        print(colored(f"\n  ... e mais {len(orphans) - 30} pastas", 'dim'))

    total_size = sum(s for _, s in orphans)
    print(colored(f"\n  Total estimado: {format_bytes(total_size)}", 'bold', bold=True))

    print()
    print(colored("  Digite números para enviar à lixeira (ex: 1,3,5)", 'dim'))
    print(colored("  [T]udo  |  [L] Ver lixeira  |  [Enter] Sair", 'dim'))
    choice = input("  Escolha: ").strip().upper()

    if choice == 'L':
        show_recycle_bin_menu()
        return

    if choice in ('', '0'):
        return

    if choice == 'T':
        selected = orphans
    else:
        indices = set()
        for part in choice.split(','):
            part = part.strip()
            if part.isdigit():
                num = int(part)
                if 1 <= num <= len(orphans):
                    indices.add(num)
        selected = [orphans[i-1] for i in sorted(indices)]

    if not selected:
        print(colored("  Nenhum item válido.", 'red'))
        input("  Pressione Enter...")
        return

    paths_to_delete = [p for p, _ in selected]
    total_sel = sum(s for _, s in selected)

    before = shutil.disk_usage(os.path.splitdrive(paths_to_delete[0])[0] + '\\')
    print(colored(f"\n  Enviando {len(selected)} pasta(s) para lixeira... (~{format_bytes(total_sel)})", 'yellow'))
    success, freed = send_to_trash(paths_to_delete)

    after = shutil.disk_usage(os.path.splitdrive(paths_to_delete[0])[0] + '\\')
    diff = after.free - before.free

    print()
    print(colored("  " + "=" * 48, 'cyan'))
    print(colored("  RESUMO DA LIMPEZA", 'green', bold=True))
    print(colored("  " + "=" * 48, 'cyan'))
    print(f"  Pastas enviadas:  {success}")
    print(f"  Espaço liberado:  {colored(format_bytes(diff), 'green', bold=True)}")
    print(f"  Espaço livre:     {format_bytes(after.free)}")
    print(colored("  " + "=" * 48, 'cyan'))
    print()

    print(colored("  [L] Ver lixeira e restaurar itens  |  [Enter] Sair", 'dim'))
    choice = input("  Escolha: ").strip().upper()
    if choice == 'L':
        show_recycle_bin_menu()


if __name__ == '__main__':
    enable_ansi()
    try:
        main()
    except KeyboardInterrupt:
        print(colored("\n\n  Programa interrompido pelo usuário.", 'yellow'))
        sys.exit(0)
