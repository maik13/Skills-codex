# Verificação e entrega

Use esta referência sempre que houver edição de código, migration, correção de dados, commit, envio ou publicação.

## Antes da alteração

- Leia `git status --short --branch` e preserve mudanças existentes.
- Identifique testes relacionados e o comportamento observável que provará a correção.
- Para banco remoto, confirme o projeto Supabase alvo. Não deduza o ambiente apenas pelo arquivo local.
- Para correção de dados, registre consulta de prévia e estratégia de reversão.

## Verificação proporcional

1. Rode testes diretamente relacionados.
2. Rode `npm run build` para alterações da aplicação.
3. Rode lint e testes amplos quando o escopo ou risco justificar. Diferencie falhas preexistentes das introduzidas.
4. Para interface, valide o fluxo real com seletores funcionais, console e respostas de rede; screenshot isolado não prova funcionamento.
5. Para desempenho, compare métricas antes/depois.
6. Para integridade, repita a consulta completa que detectou o problema.

## Supabase

- Toda mudança de schema, função, índice ou RLS deve ficar em migration versionada.
- Revise idempotência prática, locks, custo de backfill, políticas RLS e compatibilidade com código já publicado.
- Aplique primeiro em ambiente seguro quando disponível.
- Uma migration criada, mas não executada, permanece “local”. Uma chamada negada ou interrompida permanece “não aplicada”.
- Confirme o estado remoto após a aplicação; não confie apenas no retorno do cliente.

## Git e publicação

- Não faça commit, push, merge em `main`, publicação ou mensagem ao Lovable sem pedido explícito.
- Não misture alterações não relacionadas do usuário em um commit.
- Antes do envio, apresente testes executados e pendências materiais.
- Depois do envio, confirme branch e commit remoto. Publicação é uma etapa separada do push.

## Definição de concluído

Uma tarefa só está concluída quando a causa foi tratada, os consumidores relevantes foram verificados, os testes proporcionais passaram e o estado real de banco/Git/publicação foi informado sem ambiguidades.
