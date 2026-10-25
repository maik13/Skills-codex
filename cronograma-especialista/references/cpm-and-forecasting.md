# CPM e previsões

## Premissas obrigatórias

Defina antes do cálculo:

- unidade de duração;
- calendário e data-base;
- convenção de início e término;
- tipos de dependência e defasagens;
- restrições fixas;
- tratamento de atividades em andamento e concluídas.

Sem essas definições, apresente o cálculo apenas como cenário condicionado.

## Rede generalizada

Represente cada relação como uma restrição sobre o início mais cedo da sucessora `v` em relação à predecessora `u`:

- FS: `ES(v) >= ES(u) + duração(u) + lag`
- SS: `ES(v) >= ES(u) + lag`
- FF: `ES(v) >= ES(u) + duração(u) + lag - duração(v)`
- SF: `ES(v) >= ES(u) + lag - duração(v)`

Em uma rede acíclica, faça o passe para frente na ordem topológica. Use `EF = ES + duração`. No passe reverso, parta do término calculado do projeto e aplique as mesmas restrições para obter `LS` e `LF`.

- Folga total: `LS - ES`.
- Folga livre: menor margem até qualquer sucessora; para atividade terminal, margem até o término do projeto.
- Caminho crítico: atividades com folga total igual a zero dentro da tolerância numérica definida.

Uma rede com calendários diferentes por atividade exige cálculo específico por calendário; não converta silenciosamente dias úteis em corridos.

## Previsões

Use trabalho restante, produtividade observada, calendário, dependências, capacidade e bloqueios. Compare, quando possível:

- otimista: premissas favoráveis explicitadas;
- provável: produtividade e restrições observadas;
- pessimista: riscos materiais plausíveis.

Não invente probabilidades. Classifique confiança:

- **Alta:** dados completos, atuais, dependências válidas e histórico comparável.
- **Média:** pequenas lacunas ou variabilidade controlada.
- **Baixa:** lacunas relevantes, regras instáveis ou histórico fraco.
- **Não estimável:** faltam dados essenciais.

Registre os fatores que sustentam a classificação.
