# Método de auditoria

## 1. Identificação e cobertura

Antes de avaliar o cronograma, registre:

- repositório, branch e commit;
- módulos, tabelas e serviços examinados;
- ambiente e dados acessíveis;
- período, projetos e filtros;
- o que ficou fora da análise.

Compare repositórios candidatos por rotas, componentes, modelos, persistência e histórico. Um front-end integrado, protótipo, backup ou importador pode não ser a fonte de verdade.

## 2. Mapa funcional

Reconstrua:

1. origem de projetos e atividades;
2. regra de datas e duração;
3. dependências e defasagens;
4. calendário e capacidade;
5. progresso e status;
6. edição, arraste, redimensionamento e reprogramação;
7. persistência, concorrência e confirmação de gravação;
8. consumidores, filtros, relatórios e exportações.

Classifique campos e funções como implementados, parciais, ausentes ou não verificáveis.

## 3. Verificações mínimas

### Datas e calendários

- formatos inválidos, vazios e conversões UTC/local;
- início posterior ao fim;
- dias corridos versus úteis;
- inclusão das datas inicial e final;
- feriados, turnos, finais de semana e exceções;
- restrições manuais e alterações de mês ou ano.

### Dependências

- FS, SS, FF e SF realmente suportadas;
- predecessoras ausentes, autodependências, duplicatas e ciclos;
- defasagens positivas e negativas;
- propagação após mudança da predecessora;
- conflito entre dependência e data fixada.

### Progresso

- limites de 0 a 100%;
- concluído sem término real ou com quantidade incompatível;
- não iniciado com produção;
- agregação ponderada pela medida correta;
- separação entre executado e projeção.

### Persistência e segurança

- atualização otimista sem confirmação;
- erros ignorados e estados parciais;
- gravações concorrentes e perda de atualização;
- permissões no cliente sem proteção equivalente no servidor;
- mensagens entre frames sem validação de origem;
- credenciais, chaves privilegiadas ou acessos de contingência no código.

## 4. Classificação

- **Crítico:** compromete integridade, autorização ou decisão de prazo de forma abrangente.
- **Alto:** pode gerar decisão operacional errada ou atraso relevante.
- **Médio:** causa inconsistência relevante ou trabalho manual frequente.
- **Baixo:** impacto localizado.
- **Melhoria:** evolução sem defeito comprovado.
- **Inconclusivo:** indício sem evidência suficiente.

Justifique a gravidade com impacto, abrangência, probabilidade e detectabilidade.

## 5. Testes

Prefira casos pequenos com resultado matemático conhecido. Cubra, conforme aplicável:

- cadeia simples e atividades paralelas;
- marco de duração zero;
- cada tipo de dependência suportado;
- ciclo, predecessora ausente e autodependência;
- capacidade nula, equipe insuficiente e quantidade zero;
- fim de semana, feriado e fuso horário;
- alteração de duração e deslocamento com propagação;
- concorrência, persistência e falha de rede;
- volume representativo.

Teste não executado deve ser marcado como pendente.
