---
name: bambusa-system-improvement
description: Auditar e aprimorar o aplicativo Bambusa em React, Vite e Supabase quando houver lentidão, timeout, tela preta, carregamento excessivo, inconsistência entre módulos ou necessidade de verificar qualidade, integridade e regressões. Use para diagnóstico sistêmico, plano de correção ou implementação autorizada; não substitui uma alteração funcional isolada sem relação com esses riscos.
---

# Aprimoramento do Sistema Bambusa

Trate o sistema como um produto integrado. Uma tela não é uma fonte de verdade independente, e uma correção não está concluída enquanto banco, regras, interface e fluxos consumidores não estiverem coerentes e verificados.

## Limites operacionais

- O modo padrão é diagnóstico somente leitura. Pedidos para analisar, auditar ou explicar não autorizam alterar arquivos, banco, usuários, dados, publicação ou branch remota.
- Só implemente quando o usuário pedir a correção. Confirme separadamente qualquer ação que exija nova autoridade, como aplicar uma migração remota, apagar dados, publicar ou enviar ao `main`.
- Nunca use o chat do Lovable ou outro canal externo sem pedido explícito do usuário.
- Preserve alterações existentes no repositório e diferencie claramente o que já estava modificado do que esta tarefa alterou.
- Não declare “100% corrigido”, “zerado” ou “aplicado” sem uma verificação executável que cubra o universo afirmado. Permissão negada, teste não executado ou migração apenas criada devem ser relatados como pendência.

## Escolha do modo

1. **Diagnóstico:** reproduza ou meça o problema, identifique a origem e entregue evidências. Não edite.
2. **Proposta:** além do diagnóstico, apresente a menor correção suficiente, riscos, migrações e verificações. Não edite.
3. **Implementação:** altere apenas o escopo autorizado, valide proporcionalmente ao risco e informe exatamente o que foi ou não aplicado.

Se o pedido não disser o modo, infira pelo verbo: “verificar”, “entender” e “auditar” significam diagnóstico; “corrigir”, “fazer” e “implementar” autorizam implementação dentro do escopo descrito.

## Roteiro essencial

1. Leia o estado atual do Git e as instruções do repositório. Para uma avaliação sistêmica, execute `scripts/repo_health.ps1` uma vez e use o resultado apenas como triagem.
2. Delimite o universo auditado: módulo, tabelas, período, status, quantidade total e filtros. Diferencie quantidade de linhas, quantidade de entidades únicas e quantidade por regra; não some grupos sobrepostos como se fossem entidades distintas.
3. Identifique a fonte canônica de cada campo e todos os consumidores. Corrigir apenas a tela que denunciou o erro não resolve uma divergência de origem.
4. Reproduza com evidência adequada: consultas e planos para banco, métricas de renderização/rede para desempenho e seletores/estado observável para interface.
5. Antes de editar, leia a referência pertinente:
   - desempenho, timeout ou tela preta: [references/performance-and-reliability.md](references/performance-and-reliability.md);
   - códigos, vínculos, fluxos documentais ou divergências: [references/data-integrity.md](references/data-integrity.md);
   - correção, migração, testes ou envio: [references/verification-and-release.md](references/verification-and-release.md).
6. Implemente a menor mudança que elimina a causa, não apenas o sintoma. Mantenha histórico e rastreabilidade.
7. Valide o comportamento atingido, os consumidores afetados e a ausência de regressão. Para alegações globais, rode novamente a auditoria completa com os mesmos critérios e apresente os números antes/depois.

## Regras de decisão

- Uma janela operacional de 15–20 dias é uma visualização rápida, não arquivamento nem exclusão. Pendências antigas continuam visíveis, e consultas históricas devem ser solicitadas ao servidor quando houver filtro explícito.
- Evite carregar tabelas inteiras no navegador para depois filtrar, contar ou agrupar. Prefira paginação, filtros, agregações e ordenação no banco.
- Não use `networkidle` como único critério de prontidão: Supabase Realtime, WebSocket e polling podem manter conexões abertas. Aguarde um elemento ou estado funcional específico.
- Não trate códigos parecidos como a mesma entidade sem comparar o vínculo formal e os atributos determinantes. Não invente operador, processo, projeto, lote, data ou horário ausente.
- Correções em massa exigem prévia de impacto, operação auditável, possibilidade de reversão e consulta pós-correção. Preserve registros históricos; não os apague para fazer a divergência desaparecer.
- Toda transição entre Solicitação, Cotação, PN, RC e PC deve preservar a identidade do documento, os anexos, a data de necessidade e a trilha de estado. Telas diferentes devem consultar a mesma fonte canônica.

## Entrega

Comece pelo resultado. Informe o escopo realmente examinado, as evidências, a causa, o que mudou, os testes executados e o que permanece pendente. Separe explicitamente:

- correção criada localmente;
- migração aplicada ao banco;
- commit criado;
- envio ao remoto ou ao `main`;
- publicação em produção.

Nunca apresente uma dessas etapas como concluída por implicação de outra.
