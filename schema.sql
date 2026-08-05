CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE clube (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(120) NOT NULL
);

CREATE TABLE jogador (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(150) NOT NULL,
    nascimento DATE
);

CREATE TABLE vinculo (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    jogador_id UUID NOT NULL REFERENCES jogador(id),
    clube_id UUID NOT NULL REFERENCES clube(id),
    tipo VARCHAR(30) NOT NULL, -- BASE, EMPRESTIMO, RETORNO, VENDIDO...
    inicio DATE NOT NULL,
    fim DATE
);

CREATE TABLE competicao (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(120) NOT NULL,
    fase_corte VARCHAR(60) -- a partir de qual fase os minutos contam
);

CREATE TABLE partida (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    competicao_id UUID NOT NULL REFERENCES competicao(id),
    data DATE NOT NULL,
    fase VARCHAR(60) -- fase real da partida, vinda do scraping
);

CREATE TABLE participacao (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    jogador_id UUID NOT NULL REFERENCES jogador(id),
    partida_id UUID NOT NULL REFERENCES partida(id),
    minutos INT NOT NULL DEFAULT 0,
    UNIQUE (jogador_id, partida_id)
);

CREATE TABLE elegibilidade (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vinculo_id UUID NOT NULL REFERENCES vinculo(id),
    participacao_id UUID NOT NULL REFERENCES participacao(id),
    versao_regra VARCHAR(30) NOT NULL,
    elegivel BOOLEAN NOT NULL,
    UNIQUE (vinculo_id, participacao_id, versao_regra)
);

CREATE INDEX idx_vinculo_jogador ON vinculo(jogador_id);
CREATE INDEX idx_vinculo_clube ON vinculo(clube_id);
CREATE INDEX idx_partida_competicao ON partida(competicao_id);
CREATE INDEX idx_participacao_jogador ON participacao(jogador_id);
CREATE INDEX idx_participacao_partida ON participacao(partida_id);
