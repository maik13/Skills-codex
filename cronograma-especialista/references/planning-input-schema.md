# Entrada do Agente de Planejamento 2.0

Use JSON em UTF-8. Datas usam `YYYY-MM-DD`. Quantidades e pessoas podem ser fracionárias quando a operação permitir.

```json
{
  "asOfDate": "2026-10-25",
  "settings": {
    "globalStartDate": "2026-10-26",
    "globalEndDate": "2026-12-31",
    "availableTeamPerDay": 8,
    "workOnSaturdays": false,
    "workOnSundays": false,
    "holidays": ["2026-11-02"]
  },
  "projects": [
    {
      "id": "P-001",
      "name": "Projeto exemplo",
      "active": true,
      "priority": 1,
      "deadlineDate": "2026-11-20",
      "activities": [
        {
          "id": "OP-100",
          "group": "Produção",
          "processName": "Serra",
          "unit": "peça",
          "totalQuantity": 100,
          "completedQuantity": 20,
          "capacityPerDay": 25,
          "requiredPeople": 2,
          "priority": 1,
          "sequence": 1,
          "dependencies": [],
          "acceptsProportionalProduction": true
        },
        {
          "id": "OP-101",
          "group": "Produção",
          "processName": "Acabamento",
          "unit": "peça",
          "totalQuantity": 100,
          "completedQuantity": 0,
          "capacityPerDay": 20,
          "requiredPeople": 3,
          "priority": 1,
          "sequence": 2,
          "dependencies": [
            {"dependsOnId": "OP-100", "type": "FS", "lagDays": 0}
          ],
          "acceptsProportionalProduction": false
        }
      ]
    }
  ]
}
```

## Campos principais

### Configuração

- `asOfDate`: data de corte do realizado.
- `globalStartDate`: primeiro dia possível do cálculo.
- `globalEndDate`: horizonte máximo; atividade remanescente depois dele torna o plano inviável.
- `availableTeamPerDay`: limite agregado de pessoas por dia, como no motor atual do Planejamento 2.0.
- `workOnSaturdays`, `workOnSundays` e `holidays`: calendário global.

### Projeto

- `active`: projetos inativos não consomem recursos.
- `priority`: menor número é atendido primeiro.
- `startDate`: restrição opcional para o início do projeto.
- `deadlineDate`: prazo usado para alertas e desvio.

### Atividade

- `totalQuantity` e `completedQuantity`: base física do planejamento.
- `capacityPerDay`: produção da equipe completa por dia.
- `requiredPeople`: equipe necessária para a capacidade nominal.
- `acceptsProportionalProduction`: permite reduzir produção e pessoas proporcionalmente.
- `plannedStartDate`: restrição manual para não iniciar antes da data.
- `actualStartDate`, `actualEndDate` e `status`: fatos realizados; não são deslocados pelo cálculo.
- `dependencies`: relações `FS`, `SS` ou `FF`. O script também aceita `Fim-Inicio`, `Inicio-Inicio` e `Fim-Fim`.
- `lagDays`: defasagem em dias de trabalho do calendário global.

## Dados que não devem ser inventados

Quantidade, produtividade, equipe, dependência, calendário, prazo e progresso real. Quando um deles for indispensável e estiver ausente, devolva o campo faltante e o efeito da ausência.
