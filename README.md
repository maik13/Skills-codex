# Skills Codex

Repositório de skills reutilizáveis para os sistemas Bambusa, MyFinance e outros projetos Codex.

## Skill própria

- `bambusa-system-improvement`: auditoria e aprimoramento de desempenho, integridade, Supabase, interface e fluxo operacional.

## Coleção comunitária auditada

As skills em `community/` foram selecionadas por serem reutilizáveis entre projetos e possuírem licença explícita para redistribuição.

- `create-plan`: planos de implementação somente leitura.
- `gh-address-comments`: tratamento de comentários em pull requests.
- `gh-fix-ci`: diagnóstico e correção autorizada de falhas no GitHub Actions.
- `mcp-builder`: criação e avaliação de servidores MCP.
- `paperjsx`: geração de PDF, XLSX, DOCX e PPTX.
- `skill-creator`: criação de novas skills.
- `skill-installer`: instalação controlada de skills.
- `theme-factory`: temas reutilizáveis para relatórios e interfaces.
- `webapp-testing-safe`: variante endurecida para testes locais sem `shell=True` e sem dependência obrigatória de `networkidle`.

Consulte `THIRD_PARTY_NOTICES.md` e o arquivo de licença dentro de cada pasta antes de redistribuir ou modificar.

## Critério da curadoria

O catálogo de origem também contém centenas de integrações específicas de fornecedores e algumas pastas sem licença explícita. Elas não foram copiadas. Isso inclui, entre outras, skills dependentes de Composio, Notion, Linear, Datadog, LangSmith, Sentry e serviços de publicação, além de itens sem licença própria como `codebase-migrate`, `changelog-generator` e `spreadsheet-formula-helper`.

A ausência aqui não significa que a skill seja tecnicamente ruim; significa apenas que ela não atende simultaneamente aos critérios de reutilização entre os sistemas, licença verificável e risco operacional controlado.

## Uso

Instale somente a pasta necessária. Não copie toda a coleção para o contexto do Codex, pois descrições concorrentes e ferramentas não utilizadas aumentam custo e podem provocar acionamentos indevidos.
