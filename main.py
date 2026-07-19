import os
import sys
from utils import (
    clear_screen, colored, format_bytes, get_disk_usage, enable_ansi
)
from scanner import scan_top_level, scan_user_folders, drill_down
from cleaner import get_cleanup_targets, estimate_sizes, clean_targets


PROMPT = "  Escolha uma opção: "


def print_header():
    clear_screen()
    print(colored("=" * 52, 'cyan'))
    print(colored("       WIN-CLEANER — Limpeza do Sistema", 'green', bold=True))
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


def main_menu():
    while True:
        print_header()
        print("  [1] Varredura rápida (pastas do usuário)")
        print("  [2] Varredura completa (disco ou pasta)")
        print("  [3] Limpeza de lixo do sistema")
        print("  [4] Espaço livre nos discos")
        print("  [5] Sair")
        print()

        choice = input(PROMPT).strip()

        if choice == '1':
            quick_scan()
        elif choice == '2':
            full_scan()
        elif choice == '3':
            system_cleanup()
        elif choice == '4':
            show_disk_space()
        elif choice == '5':
            print(colored("\n  Até mais! 💻", 'green'))
            sys.exit(0)
        else:
            input(colored("  Opção inválida! Pressione Enter...", 'red'))


def quick_scan():
    print_header()
    print(colored("  VARREDURA RÁPIDA — Pastas do Usuário\n", 'yellow', bold=True))

    print("  Escaneando...\n")
    results, _ = scan_user_folders(progress_callback=make_progress())
    print("\n")
    show_results(results, title="PASTAS DO USUÁRIO")

    input(colored("\n  Pressione Enter para voltar ao menu...", 'dim'))


def full_scan():
    path = _ask_path()
    if path is None:
        return

    print_header()
    print(colored(f"  VARREDURA COMPLETA — {path}\n", 'yellow', bold=True))
    print("  Escaneando...\n")

    results = scan_top_level(path, progress_callback=make_progress())
    print("\n")
    show_results(results, title=f"CONTEÚDO DE {path.upper()}")

    _drill_loop(path, results)


def _ask_path():
    print_header()
    default = 'C:\\'
    path = input(colored(f"  Caminho para escanear [Enter = {default}]: ", 'yellow')).strip()
    if not path:
        path = default
    path = os.path.abspath(path)
    if not os.path.exists(path):
        input(colored(f"  Caminho não encontrado: {path}\n  Pressione Enter...", 'red'))
        return None
    return path


def _drill_loop(base_path, current_results):
    while True:
        print()
        print(colored("  [N]º para ver conteúdo da pasta  |  [V]oltar  |  [M]enu", 'dim'))
        cmd = input(PROMPT).strip().lower()

        if cmd in ('', 'm', 'menu'):
            return
        if cmd == 'v' or cmd == 'voltar':
            return
        if cmd.isdigit():
            idx = int(cmd) - 1
            if 0 <= idx < len(current_results):
                sub_path = current_results[idx][0]
                if os.path.isdir(sub_path):
                    _enter_folder(sub_path)
                else:
                    print(colored("  Não é uma pasta.", 'red'))
            else:
                print(colored("  Número inválido.", 'red'))
        else:
            print(colored("  Comando inválido.", 'red'))


def _enter_folder(path):
    print_header()
    print(colored(f"  DRILL DOWN — {path}\n", 'cyan', bold=True))
    print("  Escaneando...\n")
    results = scan_top_level(path, progress_callback=make_progress())
    print("\n")
    show_results(results, title=f"CONTEÚDO DE {path}")

    _drill_loop(path, results)


def show_results(results, title="RESULTADOS"):
    if not results:
        print(colored("  Nenhum resultado encontrado.", 'red'))
        return

    print(colored(f"  {'#':<4s} {'PASTA':<48s} {'TAMANHO':>10s}", 'cyan', bold=True))
    print(colored("  " + "-" * 64, 'cyan'))

    for i, (path, size) in enumerate(results[:25], 1):
        name = path if len(path) <= 45 else f"...{path[-42:]}"
        size_str = format_bytes(size)
        if size > 2 * 1024**3:
            cor = 'red'
        elif size > 500 * 1024**2:
            cor = 'yellow'
        else:
            cor = 'green'
        print(f"  {i:<4d} {name:<48s} {colored(size_str:>10s, cor)}")

    if len(results) > 25:
        print(colored(f"\n  ... e mais {len(results) - 25} itens", 'dim'))


def system_cleanup():
    print_header()
    print(colored("  LIMPEZA DE LIXO DO SISTEMA\n", 'yellow', bold=True))

    print("  Calculando tamanho dos alvos...\n")
    targets = get_cleanup_targets()
    targets = estimate_sizes(targets)

    available = [(i, t) for i, t in enumerate(targets, 1) if t.get('exists') and t.get('size', 0) > 0]

    if not available:
        print(colored("  Nenhum item para limpar encontrado.", 'green'))
        input("\n  Pressione Enter para voltar...")
        return

    print(colored(f"  {'Nº':<4s} {'CATEGORIA':<16s} {'ITEM':<34s} {'TAMANHO':>10s}", 'cyan', bold=True))
    print(colored("  " + "-" * 66, 'cyan'))

    for idx, t in available:
        size_str = format_bytes(t['size'])
        cor = 'red' if t['size'] > 500*1024**2 else 'yellow'
        print(f"  {idx:<4d} {t['category']:<16s} {t['name']:<34s} {colored(size_str:>10s, cor)}")

    print()
    print(colored("  Digite números separados por vírgula (ex: 1,3,5)", 'dim'))
    print(colored("  [T]udo  |  [0] Cancelar", 'dim'))
    choice = input(PROMPT).strip().upper()

    if choice in ('', '0'):
        return

    if choice == 'T':
        selected = [t[1] for t in available]
    else:
        indices = set()
        for part in choice.split(','):
            part = part.strip()
            if part.isdigit():
                num = int(part)
                if 1 <= num <= len(targets):
                    indices.add(num)
        selected = [targets[i-1] for i in sorted(indices)]

    if not selected:
        print(colored("  Nenhum item válido.", 'red'))
        input("  Pressione Enter...")
        return

    total_est = sum(t['size'] for t in selected if t.get('exists', False))
    print(colored(f"\n  Limpando {len(selected)} alvo(s) — ~{format_bytes(total_est)} estimado\n", 'yellow'))

    items, freed = clean_targets(selected)

    print(colored(f"\n  ✅  Concluído! {items} itens limpos, {format_bytes(freed)} liberados.", 'green'))
    input("\n  Pressione Enter para voltar...")


def show_disk_space():
    print_header()
    print(colored("  ESPAÇO LIVRE NOS DISCOS\n", 'yellow', bold=True))

    drives = get_disk_usage()
    if not drives:
        print(colored("  Não foi possível obter informações dos discos.", 'red'))
    else:
        print(colored(f"  {'UNIDADE':<10s} {'TOTAL':>10s} {'USADO':>10s} {'LIVRE':>10s} {'USO':>8s}", 'cyan', bold=True))
        print(colored("  " + "-" * 50, 'cyan'))
        for d in drives:
            bar_len = 14
            filled = int(bar_len * d['percent'] / 100)
            bar = '█' * filled + '░' * (bar_len - filled)
            cor = 'red' if d['percent'] > 85 else ('yellow' if d['percent'] > 60 else 'green')
            print(f"  {d['drive']:<10s} {format_bytes(d['total']):>10s} {format_bytes(d['used']):>10s} {format_bytes(d['free']):>10s} {colored(f'{d['percent']:>5.1f}%', cor):>8s}")
            print(f"  {'':<10s} [{bar}]")

    input(colored("\n  Pressione Enter para voltar...", 'dim'))


if __name__ == '__main__':
    enable_ansi()
    try:
        main_menu()
    except KeyboardInterrupt:
        print(colored("\n\n  Programa interrompido pelo usuário.", 'yellow'))
        sys.exit(0)
