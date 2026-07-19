# Roadmap — win-cleaner 2.0

## 🔴 Crítico (precisão)

- [ ] **Match real via UninstallString** — ler o caminho de instalação exato de cada programa no registro (`HKLM\...\Uninstall\{chave}\InstallLocation`) em vez de comparar nomes de pasta
- [ ] **Verificar se pasta está em uso** — tentar abrir arquivos com lock ou checar handles antes de listar como candidato
- [ ] **Cache de scan** — salvar resultados de `get_dir_size` em JSON para evitar recalcular toda vez

## 🟡 Melhorias (alcance)

- [ ] **Mais locais de varredura** — `VirtualStore`, `Start Menu\Programs`, `Tasks`, `Services`, `Environment Variables`, `PATH`
- [ ] **Scanner de lixo do Windows** — arquivos temporários, cache de navegadores, prefetch (reintegrar módulo `cleaner.py`)
- [ ] **AppData\LocalLow** — incluir na varredura

## 🟢 Experiência

- [ ] **Modo silencioso** — `--clean-all` pra limpar tudo sem interação
- [ ] **Barra de progresso detalhada** — mostrar percentual dentro de cada pasta grande
- [ ] **Reabrir lixeira** — opção de voltar pro menu após restaurar em vez de sair
- [ ] **Modo verbose** — `--verbose` pra mostrar todas as pastas ignoradas e o motivo

## 🔵 Técnico

- [ ] **Multithread no scan** — escanear pastas em paralelo (`ThreadPoolExecutor`) pra acelerar
- [ ] **Log de operações** — arquivo `.log` com data/hora do que foi limpo/restaurado
- [ ] **Empacotar como .exe** — usar PyInstaller ou Nuitka pra não precisar de Python instalado
- [ ] **Testes automatizados** — `pytest` com fixtures de mock do registro e sistema de arquivos
