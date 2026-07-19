# win-cleaner 🧹

Ferramenta que **caça e limpa pastas órfãs** deixadas por programas desinstalados no Windows. Compara pastas em `Program Files`, `ProgramData` e `AppData` contra a lista de programas instalados — tudo que não bate é candidato a lixo. Também lê a lixeira e permite restaurar itens.

## Funcionalidades

- **Caça lixo de programas desinstalados** — varre `Program Files`, `Program Files (x86)`, `ProgramData`, `AppData\Local`, `AppData\Roaming` e cruza com o Registro do Windows
- **Matching inteligente** — usa aliases de nomes (`dotnet` ↔ `.NET`, `vulkanrt` ↔ `Vulkan`) e filtro de falsos positivos
- **Envio seguro para lixeira** — usa `send2trash`, nada é deletado permanentemente
- **Leitura da lixeira** — lista itens com caminho original e permite restaurar
- **Resumo da limpeza** — mostra espaço liberado e espaço livre no disco

## Instalação

```bash
git clone https://github.com/kaua-cruz/win-cleaner.git
cd win-cleaner
pip install send2trash
python main.py
```

> ⚠️  Execute como **Administrador** para acessar todas as pastas do sistema.

## Dependências

- Python 3.7+
- [send2trash](https://github.com/arsenetar/send2trash)

## Licença

MIT
