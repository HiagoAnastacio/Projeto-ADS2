-- =======================================================================================
-- SCRIPT DE SETUP COMPLETO DO BANCO DE DADOS - Overwatch Meta Analyzer
-- (Versão Final com Suporte à Análise Temporal)
-- =======================================================================================

-- ETAPA 1: Reset completo do Schema
DROP DATABASE IF EXISTS `projeto_ads2`;
CREATE DATABASE IF NOT EXISTS `projeto_ads2` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `projeto_ads2`;

-- Desativa a verificação de chaves estrangeiras durante a criação
SET FOREIGN_KEY_CHECKS=0;

-- =======================================================================================
-- ETAPA 2: Criação de Todas as Tabelas Base (com Coluna de Timestamp)
-- =======================================================================================

-- Nível 1: Dimensões Independentes
CREATE TABLE `role` (
  `role_id` INT NOT NULL AUTO_INCREMENT,
  `role` VARCHAR(40) NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`role_id`)
);

CREATE TABLE `rank` (
  `rank_id` INT NOT NULL AUTO_INCREMENT,
  `rank_name` VARCHAR(45) NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`rank_id`)
);

CREATE TABLE `game_mode` (
  `game_mode_id` INT NOT NULL AUTO_INCREMENT,
  `game_mode_name` VARCHAR(45) NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`game_mode_id`)
);

-- Nível 2: Dimensões Dependentes
CREATE TABLE `hero` (
  `hero_id` INT NOT NULL AUTO_INCREMENT,
  `hero_name` VARCHAR(40) NOT NULL,
  `role_id` INT NOT NULL,
  `hero_icon_img_link` VARCHAR(300) DEFAULT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_id`),
  KEY `fk_role_idx` (`role_id`),
  CONSTRAINT `fk_role` FOREIGN KEY (`role_id`) REFERENCES `role` (`role_id`)
);

CREATE TABLE `map` (
  `map_id` INT NOT NULL AUTO_INCREMENT,
  `map_name` VARCHAR(45) NOT NULL,
  `game_mode_id` INT NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`map_id`),
  KEY `fk_game_mode_idx` (`game_mode_id`),
  CONSTRAINT `fk_game_mode` FOREIGN KEY (`game_mode_id`) REFERENCES `game_mode` (`game_mode_id`)
);

-- =======================================================================================
-- ETAPA 3: Criação de Tabelas de Fato (com PKs compostas para Histórico)
-- =======================================================================================

CREATE TABLE `hero_rank_map_win` (
  `hero_id` INT NOT NULL,
  `rank_id` INT NOT NULL,
  `map_id` INT NOT NULL,
  `win_rate` FLOAT NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  -- A CHAVE PRIMÁRIA AGORA INCLUI A DATA, PERMITINDO HISTÓRICO
  PRIMARY KEY (`hero_id`, `rank_id`, `map_id`, `date_of_the_data`),
  KEY `fk_hero_win_idx` (`hero_id`),
  KEY `fk_rank_win_idx` (`rank_id`),
  KEY `fk_map_win_idx` (`map_id`),
  CONSTRAINT `fk_hero_win` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`),
  CONSTRAINT `fk_rank_win` FOREIGN KEY (`rank_id`) REFERENCES `rank` (`rank_id`),
  CONSTRAINT `fk_map_win` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`)
);

CREATE TABLE `hero_rank_map_pick` (
  `hero_id` INT NOT NULL,
  `rank_id` INT NOT NULL,
  `map_id` INT NOT NULL,
  `pick_rate` FLOAT NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  -- A CHAVE PRIMÁRIA AGORA INCLUI A DATA, PERMITINDO HISTÓRICO
  PRIMARY KEY (`hero_id`, `rank_id`, `map_id`, `date_of_the_data`),
  KEY `fk_hero_pick_idx` (`hero_id`),
  KEY `fk_rank_pick_idx` (`rank_id`),
  KEY `fk_map_pick_idx` (`map_id`),
  CONSTRAINT `fk_hero_pick` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`),
  CONSTRAINT `fk_rank_pick` FOREIGN KEY (`rank_id`) REFERENCES `rank` (`rank_id`),
  CONSTRAINT `fk_map_pick` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`)
);

-- Reativa a verificação de chaves estrangeiras
SET FOREIGN_KEY_CHECKS=1;

-- =======================================================================================
-- ETAPA 4: Criação de VIEWS (para exibir o snapshot MAIS RECENTE dos dados)
-- =======================================================================================

-- 4.1. Views Base (As mais granulares, mostram apenas o último registro de cada combinação)
-- Limpo de caracteres invisíveis.

CREATE OR REPLACE VIEW `vw_hero_rank_map_win_latest` AS
WITH RankedData AS (
    SELECT 
        h.hero_id,
        r.rank_id,
        m.map_id,
        f.win_rate,
        f.date_of_the_data,
        ROW_NUMBER() OVER (
            PARTITION BY f.hero_id, f.rank_id, f.map_id 
            ORDER BY f.date_of_the_data DESC
        ) as rn
    FROM 
        hero_rank_map_win f
    JOIN hero h ON f.hero_id = h.hero_id
    JOIN  `rank` r ON f.rank_id = r.rank_id
    JOIN map m ON f.map_id = m.map_id
)
SELECT * FROM RankedData WHERE rn = 1;

CREATE OR REPLACE VIEW `vw_hero_rank_map_pick_latest` AS
WITH RankedData AS (
    SELECT 
        h.hero_id,
        r.rank_id,
        m.map_id,
        f.pick_rate,
        f.date_of_the_data,
        ROW_NUMBER() OVER (
            PARTITION BY f.hero_id, f.rank_id, f.map_id 
            ORDER BY f.date_of_the_data DESC
        ) as rn
    FROM 
        hero_rank_map_pick f
    JOIN hero h ON f.hero_id = h.hero_id
    JOIN  `rank` r ON f.rank_id = r.rank_id
    JOIN map m ON f.map_id = m.map_id
)
SELECT * FROM RankedData WHERE rn = 1;


-- 4.2. Views Agregadas (Construídas a partir das Views Base para performance e DRY)

CREATE OR REPLACE VIEW `vw_hero_rank_win` AS 
SELECT 
    hero_id, 
    rank_id, 
    AVG(win_rate) AS win_rate, 
    MAX(date_of_the_data) AS last_updated 
FROM `vw_hero_rank_map_win_latest` 
GROUP BY hero_id, rank_id;

CREATE OR REPLACE VIEW `vw_hero_rank_pick` AS 
SELECT 
    hero_id, 
    rank_id, 
    AVG(pick_rate) AS pick_rate, 
    MAX(date_of_the_data) AS last_updated 
FROM `vw_hero_rank_map_pick_latest` 
GROUP BY hero_id, rank_id;

CREATE OR REPLACE VIEW `vw_hero_map_win` AS 
SELECT 
    hero_id, 
    map_id, 
    AVG(win_rate) AS win_rate, 
    MAX(date_of_the_data) AS last_updated 
FROM `vw_hero_rank_map_win_latest` 
GROUP BY hero_id, map_id;

CREATE OR REPLACE VIEW `vw_hero_map_pick` AS 
SELECT 
    hero_id, 
    map_id, 
    AVG(pick_rate) AS pick_rate, 
    MAX(date_of_the_data) AS last_updated 
FROM `vw_hero_rank_map_pick_latest` 
GROUP BY hero_id, map_id;

CREATE OR REPLACE VIEW `vw_hero_win` AS 
SELECT 
    hero_id, 
    AVG(win_rate) AS win_rate, 
    MAX(last_updated) AS last_updated 
FROM `vw_hero_rank_win` 
GROUP BY hero_id;

CREATE OR REPLACE VIEW `vw_hero_pick` AS 
SELECT 
    hero_id, 
    AVG(pick_rate) AS pick_rate, 
    MAX(last_updated) AS last_updated 
FROM `vw_hero_rank_pick` 
GROUP BY hero_id;

-- =======================================================================================
-- ETAPA 5: SEED (INSERÇÃO DE DADOS INICIAIS NAS DIMENSÕES)
-- =======================================================================================

INSERT INTO `role` (`role`) VALUES
('DAMAGE'),
('SUPPORT'),
('TANK');

INSERT INTO `rank` (`rank_name`) VALUES
('Bronze'),
('Silver'),
('Gold'),
('Platinum'),
('Diamond'),
('Master'),
('Grandmaster and Champion');

INSERT INTO `game_mode` (`game_mode_name`) VALUES
('Control'),
('Escort'),
('Flashpoint'),
('Hybrid'),
('Push'),
('Clash');

-- =======================================================================================
-- ETAPA 6: CONFIRMAÇÃO DE CONCLUSÃO
-- =======================================================================================
SELECT 'Banco de dados recriado, tabelas, constraints, seeds e views (com suporte temporal) aplicados com sucesso.' AS status;