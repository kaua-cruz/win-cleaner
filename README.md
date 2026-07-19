# win-cleaner 🧹

Ferramenta de limpeza do Windows via terminal. Escaneia pastas, mostra o espaço ocupado e envia arquivos para a lixeira com segurança.

## Funcionalidades

- **Varredura rápida** — escaneia as pastas do usuário (Desktop, Downloads, Documents, AppData, etc.)
- **Varredura completa** — escaneia qualquer diretório ou disco inteiro com navegação interativa
- **Limpeza de lixo** — remove arquivos temporários do Windows, cache de navegadores, prefetch e mais
- **Espaço nos discos** — mostra uso de todas as unidades com barra visual

## Instalação

```bash
git clone https://github.com/seu-usuario/win-cleaner.git
cd win-cleaner
pip install send2trash
python main.py
```

> ⚠️  Para limpar pastas do sistema (Windows Temp, Prefetch), execute como **Administrador**.

## Dependências

- Python 3.7+
- [send2trash](https://github.com/arsenetar/send2trash) — envia arquivos para a lixeira do Windows com segurança

## Licença

MIT
