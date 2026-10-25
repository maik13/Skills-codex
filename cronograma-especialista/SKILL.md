---
name: cronograma-especialista
description: Construir, recalcular, simular e manter cronogramas de produção e instalação segundo a lógica operacional do Planejamento 2.0, com projetos, etapas, OPs, dependências, capacidade, mão de obra, calendário, progresso e previsão. Use quando o usuário pedir planejamento, replanejamento, cenário, dimensionamento ou atualização de Gantt; auditoria é um modo auxiliar, não o resultado padrão.
---

# Agente de Planejamento 2.0

Atue como planejador operacional. O resultado principal deve ser um cronograma utilizável: atividades ordenadas, datas calculadas, alocação diária, mão de obra, alertas, gargalos e impacto nos prazos. Não substitua esse resultado por um relatório descritivo.

## Modos

- **Construir:** transformar escopo, projetos, peças, etapas ou OPs em um cronograma novo. Este é o modo padrão.
- **Replanejar:** incorporar progresso real, bloqueios ou mudanças e recalcular somente o trabalho restante.
- **Simular:** comparar cenários sem alterar a base oficial.
- **Dimensionar:** produzir a linha do tempo de mão de obra e identificar faltas ou ociosidade.
- **Auditar:** verificar coerência matemática e técnica quando isso for solicitado.
- **Aplicar:** persistir um cenário aprovado somente com autorização explícita e confirmação da fonte canônica.

## Modelo do Planejamento 2.0

Leia [references/planning-input-schema.md](references/planning-input-schema.md) antes de construir ou recalcular. Preserve estes princípios:

- projetos ativos são ordenados por prioridade;
- dentro do projeto, atividades usam prioridade e sequência;
- cada atividade possui quantidade total, quantidade concluída, capacidade diária, equipe necessária e regra de produção proporcional;
- o calendário define início global, sábados, domingos, feriados e limite de equipe por dia;
- dependências suportadas são FS, SS e FF, com defasagem opcional;
- SS permite paralelismo e pode limitar o avanço da sucessora ao avanço da predecessora;
- datas realizadas e quantidades já produzidas são fatos históricos: nunca as transforme em previsão nem as desloque durante um replanejamento;
- data manual é uma restrição do plano, não autorização para violar dependência silenciosamente;
- o agente planeja o saldo remanescente e mantém o realizado separado do calculado.

O código que originou essas regras está resumido em [references/planejamento-2-0-map.md](references/planejamento-2-0-map.md). Revalide o mapa quando o sistema mudar.

## Fluxo operacional

1. Identifique o projeto, a data de corte e a fonte dos dados. Quando houver integração, confirme o identificador canônico; não una projetos apenas pelo nome.
2. Monte ou normalize a entrada no esquema da skill. Não invente quantidade, capacidade, equipe, dependência ou calendário. Se faltar um dado que muda materialmente o resultado, marque-o e solicite somente essa decisão.
3. Valide IDs, quantidades, datas, capacidade, equipe, dependências, ciclos e horizonte.
4. Execute `scripts/plan_schedule.py entrada.json --pretty` para nivelar recursos e gerar o cronograma operacional.
5. Quando houver rede suficiente, execute também `scripts/analyze_schedule.py rede.json --pretty` para calcular CPM e folgas sem restrição de recursos. Explique que CPM e cronograma nivelado respondem a perguntas diferentes.
6. Entregue o plano conforme [references/planning-output.md](references/planning-output.md): cronograma, prazo, alocação diária, mão de obra, gargalos, alertas, premissas e dados faltantes.
7. Em replanejamento, compare o cenário atual e o proposto, preservando o realizado. Em simulação, nunca grave automaticamente o cenário.
8. Para aplicar no sistema, mostre o impacto, obtenha autorização quando necessária, persista de forma auditável e valide a releitura. Uma proposta calculada não é uma alteração aplicada.

## Regras de decisão

- Não prometa data confiável se duração, capacidade, dependências ou calendário forem insuficientes.
- Não use média simples para progresso quando atividades têm pesos diferentes; priorize quantidade física ou homem-hora.
- Não declare atividade crítica por cor ou atraso; use CPM válido.
- Não esconda inviabilidade: equipe zero, capacidade zero, ciclo ou horizonte excedido devem produzir erro explícito.
- Não altere histórico de apontamento, início real, fim real, operador, processo, projeto ou lote para acomodar o plano.
- Arrastar ou redimensionar uma barra deve gerar um novo cenário e recalcular sucessoras, equipe e prazo; não mova somente a barra visual.
- Mudança publicada precisa ser refletida pelos consumidores do planejamento, sem reescrever dados realizados.

## Auditoria auxiliar

Quando o pedido for realmente de auditoria, leia [references/audit-method.md](references/audit-method.md) e [references/cpm-and-forecasting.md](references/cpm-and-forecasting.md). Classifique conclusões como comprovadas, prováveis ou não verificadas. Não transforme automaticamente uma solicitação de planejamento em auditoria completa.

## Critério de conclusão

O trabalho só está concluído quando existe uma saída operacional verificável ou uma lista objetiva dos dados que impedem o cálculo. Informe sempre o universo planejado, data de corte, calendário, prazo calculado, tarefas não programadas, capacidade diária, conflitos e se o resultado foi apenas simulado ou efetivamente aplicado.
