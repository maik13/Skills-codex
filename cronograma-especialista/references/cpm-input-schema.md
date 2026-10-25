# Entrada do calculador CPM

Use `scripts/analyze_schedule.py` somente quando todas as durações estiverem na mesma unidade e o calendário já tiver sido normalizado.

## Formato

```json
{
  "activities": [
    {
      "id": "A",
      "duration": 3,
      "dependencies": []
    },
    {
      "id": "B",
      "duration": 2,
      "dependencies": [
        { "predecessor": "A", "type": "FS", "lag": 0 }
      ]
    }
  ]
}
```

Tipos aceitos: `FS`, `SS`, `FF` e `SF`. `lag` é opcional e usa a mesma unidade das durações. Duração zero é válida para marcos.

## Execução

```text
python scripts/analyze_schedule.py arquivo.json --pretty
```

O resultado inclui erros de integridade, ordem topológica, duração calculada, ES, EF, LS, LF, folga total, folga livre e indicação de criticidade.

O script não interpreta datas, feriados, turnos, produtividade, progresso ou restrições específicas do aplicativo. Faça essa normalização antes e documente as premissas.
