# Mapa do Planejamento 2.0 — Bambusa

Atualizado em 2026-10-25. Revalide este mapa quando os commits mudarem.

## Fontes examinadas

### Integração no Fluxo de Estoque

- Repositório local: `maik13/fluxo-estoque-dinamico`.
- Commit examinado: `8bf9780b63e1437ad50e13b08b2b98b7b6a08e35`.
- A branch local estava dois commits à frente de `origin/main` e a pasta `.codex` já estava não rastreada.
- Entrada de navegação: `src/pages/Index.tsx` e `src/components/gestao-estoque/NavegacaoLateralEstoque.tsx`.
- Lista e criação de workspaces: `src/components/integracoes/Planejamento2Integrado.tsx`.
- Atividades e ligação com produção: `src/components/integracoes/Planejamento2WorkspaceIntegrado.tsx`.
- Sessão separada do App Controle: `src/components/integracoes/AppControleSessionGate.tsx`.
- Cliente remoto: `src/integrations/appcontrole/client.ts`.

A integração lê e grava `planejamento_v2_workspaces`, `planejamento_v2_tasks` e `planejamento_v2_dependencies` em um projeto Supabase do App Controle. Ela também consulta `producao_projetos`, `producao_ordens_producao` e `producao_apontamentos` no banco do Fluxo.

### Aplicativo de planejamento

- Repositório privado: `maik13/v0-planejamento-producao-bambusa`.
- Commit examinado: `d69fbe933bec43f5f26dc327789dca54576c5862`.
- Gantt: `app/(app)/gantt/page.tsx` e `components/gantt-chart.tsx`.
- Motor: `lib/engine/scheduler.ts`.
- Estado e persistência: `lib/store.ts`.
- Tipos: `types/index.ts` e `lib/types/database.ts`.
- Simulação: `lib/engine/miop.ts`.
- Importação: `lib/supabase/import-advanced.ts`.

O estado operacional do aplicativo é persistido por Zustand em LocalForage e, quando incorporado, sincronizado com a janela pai por `postMessage`. Há código de importação para tabelas Supabase, mas a inspeção não comprovou que essas tabelas sejam a fonte usada pelo Gantt em execução.

## Lógica operacional capturada pela skill

O motor examinado simula a produção dia a dia. A skill preserva a essência operacional e corrige os pontos que impediriam um agente confiável:

- considera somente projetos ativos;
- ordena por prioridade do projeto, prioridade da atividade e sequência;
- planeja o saldo entre quantidade total e quantidade concluída;
- limita o consumo à equipe global disponível por dia;
- reduz capacidade proporcionalmente quando a atividade permite equipe parcial;
- mantém produção fixa quando a atividade exige equipe completa;
- respeita sábados, domingos e feriados configurados;
- trata FS, SS e FF explicitamente e rejeita predecessora ausente, autodependência, duplicata e ciclo;
- preserva datas e quantidades realizadas e grava a previsão em campos calculados separados;
- interrompe com estado inviável e alerta explícito quando o horizonte termina com saldo;
- devolve alocação diária, utilização da equipe, prazo por projeto e carga por processo.

O motor atual usa equipe agregada. Cadastro individual, função profissional, turno e custo não participam do nivelamento enquanto esses dados não forem fornecidos por outra fonte.

## Ambiguidade canônica

Os dois repositórios apresentam modelos de dados diferentes:

- a integração usa tabelas `planejamento_v2_*`;
- o aplicativo de planejamento usa objetos Zustand e nomes `planejamento_*` no importador.

Até confirmar o contrato de incorporação e o banco real, trate a fonte de verdade como **não verificada**. Não combine os modelos nem aplique correções cruzadas por nome de projeto.

## Pontos obrigatórios antes de aplicar um plano

1. Confirmar commit e ambiente implantado.
2. Confirmar qual persistência alimenta o Gantt publicado.
3. Obter esquema, RLS, funções e histórico das tabelas efetivamente usadas.
4. Simular arraste, dependências e recálculo com um projeto isolado antes de persistir.
5. Confirmar calendários, linha de base, defasagens e convenção de datas.
6. Não modificar dados reais durante simulação; aplicar somente o cenário aprovado e reler a persistência.
