# Integridade dos dados e fluxos

Use esta referência para OPs, apontamentos, vínculos formais, operadores, processos, projetos, lotes e documentos de estoque/compra.

## Auditoria completa

- Declare a granularidade de cada tabela antes de comparar: cadastro formal, documento, item, apontamento, evento ou ciclo.
- Normalize apenas para comparação; preserve o valor original na evidência.
- Produza três números distintos: linhas afetadas, entidades únicas afetadas e ocorrências por regra.
- Categorias podem se sobrepor. Mostre a interseção ou calcule um conjunto único; não apresente a soma das categorias como total definitivo.
- Use a mesma consulta e os mesmos critérios no antes/depois. Se o critério mudou, explique por que os números não são diretamente comparáveis.

## OP e produção

- Diferencie código exibido, cadastro formal e vínculo interno por ID.
- Códigos como `OP 2510`, `OP OP 2510` e variantes de espaço só podem ser consolidados após confirmar que representam a mesma entidade.
- Audite ciclos como pares de eventos conforme a regra vigente do módulo. Liste entradas sem fim, fins sem entrada, múltiplos candidatos e vínculos com código formal diferente.
- Não escolha silenciosamente operador, processo, projeto, lote, data ou horário quando existirem candidatos divergentes.
- Uma retificação deve preservar a trilha de auditoria e não criar novo ciclo, novo cadastro ou apontamento órfão sem necessidade.

## Solicitação e compras

- Solicitação, Cotação, PN, RC e PC formam um fluxo documental integrado; a mudança de estado não deve criar versões independentes da mesma entidade.
- Preserve itens, quantidades, unidade, projeto/centro de custo, data de necessidade, solicitante, anexos e histórico de edição.
- Todas as telas que representam o mesmo tipo de documento devem consultar a mesma fonte canônica, respeitando permissões.
- Uma cotação só avança para PN quando cumprir a aprovação exigida pela regra vigente. Arquivamento deve manter consulta histórica e motivo.

## Correção em massa

1. Gere uma consulta de prévia com ID, estado antigo, estado proposto e motivo.
2. Valide cardinalidade e conflitos antes da escrita.
3. Prefira transação, migration versionada ou rotina explicitamente auditável.
4. Preserve histórico e prepare reversão proporcional ao impacto.
5. Execute consulta pós-correção e compare com a mesma regra da prévia.
6. Relate separadamente registros corrigidos, ignorados, conflitantes e falhos.

Nunca transforme ausência de evidência em valor padrão e nunca apague dados apenas para zerar um relatório.
