---
name: webapp-testing-safe
description: Testar aplicações web locais ou explicitamente autorizadas com Playwright, verificando fluxos, erros do console, respostas de rede e regressões sem executar comandos por shell nem depender de networkidle.
license: Complete terms in LICENSE.txt
---

<!-- Modified derivative of composio-community/awesome-codex-skills webapp-testing, 2026-10-24. -->

# Testes seguros de aplicações web

Use esta skill para reproduzir defeitos de interface, validar fluxos e verificar regressões em aplicações locais ou em ambientes que o usuário autorizou testar.

## Limites

- Não teste domínios, contas ou dados fora do escopo fornecido pelo usuário.
- Não use credenciais reais sem autorização explícita.
- Testes de diagnóstico são somente leitura. Só efetue cadastros, exclusões, pagamentos ou outras mutações quando elas fizerem parte do fluxo autorizado.
- Capture evidências sem expor tokens, senhas, cookies ou dados pessoais.

## Servidor local

O helper `scripts/with_server.py` recebe comandos como vetores JSON e sempre usa `shell=False`. Execute `--help` antes do primeiro uso.

Exemplo:

```powershell
python scripts/with_server.py `
  --server-json '["npm","run","dev","--","--host","127.0.0.1","--port","5173"]' `
  --port 5173 `
  -- python teste_playwright.py
```

Repita `--server-json` e `--port` para iniciar mais de um serviço.

## Estratégia do teste

1. Defina o comportamento observável que comprova sucesso ou falha.
2. Abra a página e aguarde um seletor, texto, URL ou resposta específica. Não use `networkidle` como único critério: Realtime, WebSocket e polling podem manter a rede ativa.
3. Capture erros do console, exceções de página e respostas HTTP 4xx/5xx.
4. Use seletores por papel, rótulo ou identificador estável; evite coordenadas e classes visuais frágeis.
5. Execute o menor fluxo capaz de reproduzir o problema.
6. Ao final, feche o navegador e informe passos, resultado, evidências e limitações.

## Evidência mínima

- URL/ambiente testado;
- estado inicial;
- ações executadas;
- resultado esperado e observado;
- erros de console ou rede;
- screenshot apenas quando ele acrescentar informação.

Uma tela renderizada não prova que o fluxo funciona. Valide o estado de dados ou a resposta funcional correspondente.
