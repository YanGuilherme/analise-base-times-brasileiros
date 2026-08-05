# Minutagem da Base — Spec

## Ideia principal

Automatizar (e manter atualizado) o levantamento de minutagem de jogadores formados na base dos 12 principais clubes do Brasil, hoje feito manualmente em Excel. O objetivo é um dashboard aberto, escalável e fácil de manter, que substitua o trabalho manual sem alterar a metodologia original.

Projeto **open source**, sem monetização. Intenção de contatar Guilherme Frossard / Hugo Lobão, oferecendo o código e o site prontos, dando os devidos créditos pela metodologia.

## Inspiração

Vídeo do canal do Frossard (jornalista do Galo) em que Hugo Lobão detalha, entre 4:28–7:24, a metodologia usada para o levantamento de minutagem dos atletas da base nos 12 principais clubes brasileiros. Fonte de dados original: **Ogol** (site português de estatísticas de futebol).

### Regras da metodologia original (via transcrição do vídeo)

- Conta apenas jogadores **formados no clube**.
- Se o jogador saiu (emprestado, por exemplo) e voltou, só é desconsiderado se a saída foi **longa**. Empréstimo curto pra ganhar minutagem e volta: conta normal.
- Jogador vendido que sai e depois retorna (não por empréstimo): **não conta**.
- Fonte: Ogol — **não considera minutos de acréscimo**, para nenhum clube (particularidade da fonte, não da metodologia).
- Recorte temporal por competição:
  - Estaduais: só a partir da **fase final** (primeira fase é ignorada, pois times jogam alternativos).
  - Competições nacionais e internacionais contam **por inteiro**: Brasileirão, Copa do Brasil, Libertadores, Sul-Americana, Recopa, Supercopa.

## Decisões de implementação (arquitetura)

- **Sem Saga/filas**: diferente do Custódia Digital, este domínio não tem transação distribuída — os dados mudam só após cada rodada, então o desenho é de **job batch agendado**, não streaming.
- **Postgres como fonte da verdade**: dado relacional, precisa de integridade e consultas ad-hoc (joins, filtros por fase/competição). Redis pode entrar depois só como cache de leitura, não como armazenamento primário.
- **Camada de coleta separada da camada de regras**: scraper do Ogol isolado como adapter, para poder trocar de fonte de dados no futuro sem afetar a lógica de elegibilidade.
- **Regras de elegibilidade como Strategy/Factory**: cada critério (tipo de vínculo, corte de fase, etc.) plugável e testável isoladamente, já que os critérios podem ser revistos entre temporadas.
- **Persistência do resultado calculado (elegibilidade)**: feita durante o job batch pós-rodada, não recalculada on-the-fly a cada acesso ao dashboard. Cada registro de elegibilidade guarda a **versão da regra** usada, garantindo histórico auditável mesmo que os critérios mudem depois.
- **Scraping do Ogol**: sem API oficial encontrada. Vai ser via parsing de HTML, com volume de requisições baixo (12 clubes, atualização pós-rodada) — sem necessidade de bater forte no site. Se não for viável, buscar fonte alternativa confiável.

## Modelo de dados (simplificado)

Entidades: `clube`, `jogador`, `vinculo` (entidade própria, com tipo/início/fim), `competicao` (com `fase_corte`), `partida` (com `fase` real vinda do scraping), `participacao` (minutos por jogador/partida), `elegibilidade` (referencia vínculo + participação + versão da regra).

- `fase_corte` (em `competicao`) é **string**, não data: representa a fase a partir da qual os minutos contam (ex: "fase final"), pois a data exata dessa fase muda a cada edição do campeonato. A data real de cada partida fica em `partida.data`, junto com a `fase` daquela partida específica (dado que vem do Ogol/scraping).
- Diagrama ER já desenhado e discutido no chat.

## Stack já validada

- Docker Compose com Postgres 16, schema.sql aplicado via `docker-entrypoint-initdb.d`.
- Job batch de atualização: reaproveitar experiência prévia com disparo de jobs agendados em Java (já feito antes para envio de e-mails).

## Dúvidas discutidas e resolvidas

1. **Por que entidade `vinculo` própria, e não embutida em `jogador`?** — Para guardar histórico de vínculos (base, empréstimo, retorno, venda) como registros distintos, permitindo reconstruir a linha do tempo de cada jogador.
2. **Quando persistir a elegibilidade calculada?** — No momento do job batch pós-rodada, junto da atualização de vínculos e minutos, e não sob demanda no dashboard — por auditabilidade e performance.
3. **Por que Postgres e não Redis como base principal?** — Postgres é fonte da verdade (dado relacional, precisa de joins/consultas complexas e consistência); Redis serviria só como cache de resultados já calculados.
4. **Por que `fase_corte` é string e não date?** — Porque representa uma fase da competição (relativa), não uma data fixa; a data real vem da tabela `partida`, associada a cada edição do campeonato.
5. **A fonte de dados (Ogol) fornece a fase da partida?** — Sim, normalmente identifica a fase/rodada de cada jogo no scraping. Mas o `fase_corte` (a partir de qual fase contar) é uma decisão da metodologia, não algo que o Ogol entrega pronto — precisa ser configurado por competição/temporada.

## Próximos passos em aberto

- Validar viabilidade do scraping do Ogol (estrutura do HTML, robustez do parser).
- Refinar critério de "empréstimo longo" com o Hugo Lobão/Frossard antes de publicar (pedir revisão da lógica de negócio).
- Desenhar o job batch de atualização pós-rodada (linguagem/stack a definir — Java já usado antes para jobs agendados).
- Definir front-end do dashboard (ainda não discutido).
- Preparar contato por e-mail com Frossard/Hugo Lobão: oferecer código + site prontos, dar crédito à metodologia original, propor uso contínuo como ferramenta de trabalho deles.
