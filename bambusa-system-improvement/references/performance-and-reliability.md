# Desempenho e confiabilidade

Use esta referência para lentidão, timeout, tela preta, consumo excessivo de memória, listas grandes e falhas intermitentes de carregamento.

## Diagnóstico

1. Meça separadamente autenticação, primeira resposta, consultas ao Supabase, transformação em JavaScript e renderização.
2. Registre quantidade de chamadas, linhas retornadas, tamanho aproximado do payload, tempo de cada consulta e renderizações repetidas.
3. Procure por `select('*')` sem limite, loops com consultas, carregamentos disparados por múltiplos componentes, invalidações amplas e efeitos com dependências instáveis.
4. Verifique se cartões, contagens e relatórios baixam registros completos apenas para calcular totais no navegador.
5. Para tela preta, capture erro de console, promessa rejeitada, estado de autenticação, expiração/renovação de sessão e resposta das consultas críticas. A interface deve possuir erro recuperável e limite de espera; nunca permanecer indefinidamente vazia.

## Estratégia de dados

- Listas operacionais devem começar com período curto e paginação no servidor.
- Registros pendentes ou abertos são exceções ao corte temporal e permanecem visíveis.
- Histórico completo só deve ser buscado mediante período, identificador ou filtro explícito.
- Agregações de painel devem vir de consulta agregada, view ou RPC, em vez de transferir todas as linhas.
- Use índices alinhados a filtros, junções e ordenação reais. Antes de propor um índice, confirme seletividade, índice existente e impacto de escrita.
- Em análise de plano, use comandos somente leitura. Não execute `EXPLAIN ANALYZE` sobre comandos mutáveis.
- Mantenha RLS e escopo por usuário/projeto nas consultas otimizadas; desempenho não autoriza ampliar acesso.

## React e TanStack Query

- A `queryKey` deve conter todos os filtros que mudam o resultado.
- Cancele ou ignore respostas obsoletas ao trocar filtros rapidamente.
- Faça debounce de busca textual e preserve a página anterior enquanto a próxima carrega quando isso não confundir o usuário.
- Invalide apenas consultas afetadas após uma mutação; evite recarregar catálogo, saldos e histórico completos.
- Não armazene grandes coleções operacionais em um contexto global quando apenas uma tela as utiliza.
- Lazy-load módulos e bibliotecas pesadas que não são necessários na tela inicial.
- Virtualize tabelas extensas somente depois de paginar no servidor; virtualização não reduz payload.

## Teste de interface

- Espere por um seletor ou texto que represente o estado funcional esperado.
- Capture erros do console e respostas 4xx/5xx.
- Teste carregamento inicial, filtro, paginação, mutação e recuperação após falha.
- Para fluxos com Realtime ou polling, não dependa de `networkidle`.

## Critério de melhora

Compare antes/depois com a mesma conta, filtro, base e ambiente. Relate pelo menos tempo percebido, chamadas críticas e linhas retornadas. Uma compilação bem-sucedida não comprova melhora de desempenho.
