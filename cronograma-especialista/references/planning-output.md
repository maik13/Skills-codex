# Saída operacional do Agente de Planejamento

O agente deve entregar primeiro o plano, não uma narrativa de auditoria.

## 1. Resultado executivo

- data de corte;
- início e conclusão calculados;
- projetos dentro e fora do prazo;
- equipe máxima, pico utilizado e necessidade adicional;
- tarefas não programadas ou inviáveis.

## 2. Cronograma

Uma linha por projeto, etapa ou OP com, no mínimo:

- projeto e prioridade;
- atividade, grupo e processo;
- quantidade total, realizada e remanescente;
- início e fim calculados;
- duração em dias trabalhados;
- equipe nominal e capacidade diária;
- predecessoras;
- situação e alerta.

## 3. Linha do tempo de mão de obra

Uma linha por dia ou semana contendo pessoas disponíveis, utilizadas, ociosas e demanda não atendida. Quando houver funções como mestre, oficial e ajudante nos dados de origem, apresente-as separadamente; o motor atual usa apenas o total agregado e essa limitação deve ficar visível.

## 4. Gargalos e conflitos

Liste processos com maior carga, dias de capacidade saturada, dependências bloqueadoras, datas manuais conflitantes, atrasos previstos e atividades que não couberam no horizonte.

## 5. Cenários

Para cada cenário, mostre apenas variáveis alteradas, nova conclusão, diferença de prazo, mudança de mão de obra e efeitos colaterais. Nunca aplique automaticamente o melhor cenário.

## 6. Estado da ação

Finalize com um rótulo inequívoco:

- `SIMULADO`: calculado fora da base oficial;
- `PROPOSTO`: pronto para aprovação;
- `APLICADO E VALIDADO`: persistido e relido no sistema;
- `BLOQUEADO`: faltam dados ou autorização.
