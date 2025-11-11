-- =======================================================================================
-- SCRIPT DE SETUP COMPLETO DO BANCO DE DADOS - Overwatch Meta Analyzer
-- (v0.6.0 - Adicionadas tabelas hero_game_mode_rank_win/pick e views _latest correspondentes)
-- =======================================================================================

-- ETAPA 1: Reset completo do Schema
DROP DATABASE IF EXISTS `Projeto_ADS2`;
CREATE DATABASE IF NOT EXISTS `Projeto_ADS2` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE `Projeto_ADS2`;

SET FOREIGN_KEY_CHECKS=0;

-- =======================================================================================
-- ETAPA 2: Criação de Tabelas de Dimensão (COM Surrogate Key ID e UNIQUE Key no Nome)
-- =======================================================================================

CREATE TABLE `role` (
  `role_id` INT NOT NULL AUTO_INCREMENT,
  `role` VARCHAR(40) NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`role_id`),
  UNIQUE KEY `uq_role_name` (`role`)
) COMMENT='Funções dos heróis';

CREATE TABLE `rank` (
  `rank_id` INT NOT NULL AUTO_INCREMENT,
  `rank_name` VARCHAR(45) NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`rank_id`),
  UNIQUE KEY `uq_rank_name` (`rank_name`)
) COMMENT='Ranks (Grandmaster agrupa os níveis mais altos)';

CREATE TABLE `game_mode` (
  `game_mode_id` INT NOT NULL AUTO_INCREMENT,
  `game_mode_name` VARCHAR(45) NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`game_mode_id`),
  UNIQUE KEY `uq_game_mode_name` (`game_mode_name`)
) COMMENT='Modos de jogo';

CREATE TABLE `hero` (
  `hero_id` INT NOT NULL AUTO_INCREMENT,
  `hero_name` VARCHAR(40) NOT NULL,
  `role_id` INT NOT NULL,
  `hero_icon_img_link` VARCHAR(300) DEFAULT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_id`),
  UNIQUE KEY `uq_hero_name` (`hero_name`),
  KEY `fk_hero_role_idx` (`role_id`),
  CONSTRAINT `fk_hero_role` FOREIGN KEY (`role_id`) REFERENCES `role` (`role_id`)
) COMMENT='Heróis do jogo';

CREATE TABLE `map` (
  `map_id` INT NOT NULL AUTO_INCREMENT,
  `map_name` VARCHAR(45) NOT NULL,
  `game_mode_id` INT NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`map_id`),
  UNIQUE KEY `uq_map_name` (`map_name`),
  KEY `fk_map_game_mode_idx` (`game_mode_id`),
  CONSTRAINT `fk_map_game_mode` FOREIGN KEY (`game_mode_id`) REFERENCES `game_mode` (`game_mode_id`)
) COMMENT='Mapas do jogo';

-- =======================================================================================
-- ETAPA 3: Tabelas de Fato (Históricas, Separadas por Métrica/Agregação)
-- Usam ID PK Surrogate + UNIQUE KEY Natural (Contexto + Data)
-- =======================================================================================

-- Agregação por Herói
CREATE TABLE `hero_win` (
  `hero_win_id` INT NOT NULL AUTO_INCREMENT,
  `hero_id` INT NOT NULL,
  `win_rate` FLOAT NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_win_id`),
  UNIQUE KEY `uq_hero_win_snapshot` (`hero_id`, `date_of_the_data`),
  CONSTRAINT `fk_hw_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`)
) COMMENT='Histórico de Win Rate agregado por Herói';

CREATE TABLE `hero_pick` (
  `hero_pick_id` INT NOT NULL AUTO_INCREMENT,
  `hero_id` INT NOT NULL,
  `pick_rate` FLOAT NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_pick_id`),
  UNIQUE KEY `uq_hero_pick_snapshot` (`hero_id`, `date_of_the_data`),
  CONSTRAINT `fk_hp_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`)
) COMMENT='Histórico de Pick Rate agregado por Herói';

-- Agregação por Herói e Rank
CREATE TABLE `hero_rank_win` (
  `hero_rank_win_id` INT NOT NULL AUTO_INCREMENT,
  `hero_id` INT NOT NULL,
  `rank_id` INT NOT NULL,
  `win_rate` FLOAT NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_rank_win_id`),
  UNIQUE KEY `uq_hero_rank_win_snapshot` (`hero_id`, `rank_id`, `date_of_the_data`),
  CONSTRAINT `fk_hrw_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`),
  CONSTRAINT `fk_hrw_rank` FOREIGN KEY (`rank_id`) REFERENCES `rank` (`rank_id`)
) COMMENT='Histórico de Win Rate agregado por Herói e Rank';

CREATE TABLE `hero_rank_pick` (
  `hero_rank_pick_id` INT NOT NULL AUTO_INCREMENT,
  `hero_id` INT NOT NULL,
  `rank_id` INT NOT NULL,
  `pick_rate` FLOAT NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_rank_pick_id`),
  UNIQUE KEY `uq_hero_rank_pick_snapshot` (`hero_id`, `rank_id`, `date_of_the_data`),
  CONSTRAINT `fk_hrp_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`),
  CONSTRAINT `fk_hrp_rank` FOREIGN KEY (`rank_id`) REFERENCES `rank` (`rank_id`)
) COMMENT='Histórico de Pick Rate agregado por Herói e Rank';

-- Agregação por Herói e Mapa
CREATE TABLE `hero_map_win` (
  `hero_map_win_id` INT NOT NULL AUTO_INCREMENT,
  `hero_id` INT NOT NULL,
  `map_id` INT NOT NULL,
  `win_rate` FLOAT NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_map_win_id`),
  UNIQUE KEY `uq_hero_map_win_snapshot` (`hero_id`, `map_id`, `date_of_the_data`),
  CONSTRAINT `fk_hmw_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`),
  CONSTRAINT `fk_hmw_map` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`)
) COMMENT='Histórico de Win Rate agregado por Herói e Mapa';

CREATE TABLE `hero_map_pick` (
  `hero_map_pick_id` INT NOT NULL AUTO_INCREMENT,
  `hero_id` INT NOT NULL,
  `map_id` INT NOT NULL,
  `pick_rate` FLOAT NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_map_pick_id`),
  UNIQUE KEY `uq_hero_map_pick_snapshot` (`hero_id`, `map_id`, `date_of_the_data`),
  CONSTRAINT `fk_hmp_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`),
  CONSTRAINT `fk_hmp_map` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`)
) COMMENT='Histórico de Pick Rate agregado por Herói e Mapa';

-- Agregação por Herói e Modo de Jogo
CREATE TABLE `hero_game_mode_win` (
  `hero_game_mode_win_id` INT NOT NULL AUTO_INCREMENT,
  `hero_id` INT NOT NULL,
  `game_mode_id` INT NOT NULL,
  `win_rate` FLOAT NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_game_mode_win_id`),
  UNIQUE KEY `uq_hero_gm_win_snapshot` (`hero_id`, `game_mode_id`, `date_of_the_data`),
  CONSTRAINT `fk_hgw_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`),
  CONSTRAINT `fk_hgw_gm` FOREIGN KEY (`game_mode_id`) REFERENCES `game_mode` (`game_mode_id`)
) COMMENT='Histórico de Win Rate agregado por Herói e Modo de Jogo';

CREATE TABLE `hero_game_mode_pick` (
  `hero_game_mode_pick_id` INT NOT NULL AUTO_INCREMENT,
  `hero_id` INT NOT NULL,
  `game_mode_id` INT NOT NULL,
  `pick_rate` FLOAT NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_game_mode_pick_id`),
  UNIQUE KEY `uq_hero_gm_pick_snapshot` (`hero_id`, `game_mode_id`, `date_of_the_data`),
  CONSTRAINT `fk_hgp_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`),
  CONSTRAINT `fk_hgp_gm` FOREIGN KEY (`game_mode_id`) REFERENCES `game_mode` (`game_mode_id`)
) COMMENT='Histórico de Pick Rate agregado por Herói e Modo de Jogo';

-- Tabela Granular (Herói, Rank, Mapa)
CREATE TABLE `hero_rank_map_win` (
  `hero_rank_map_win_id` BIGINT NOT NULL AUTO_INCREMENT,
  `hero_id` INT NOT NULL,
  `rank_id` INT NOT NULL,
  `map_id` INT NOT NULL,
  `win_rate` FLOAT NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_rank_map_win_id`),
  UNIQUE KEY `uq_hero_rank_map_win_snapshot` (`hero_id`, `rank_id`, `map_id`, `date_of_the_data`),
  CONSTRAINT `fk_hrmw_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`),
  CONSTRAINT `fk_hrmw_rank` FOREIGN KEY (`rank_id`) REFERENCES `rank` (`rank_id`),
  CONSTRAINT `fk_hrmw_map` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`)
) COMMENT='Histórico granular de Win Rate por Herói/Rank/Mapa';

CREATE TABLE `hero_rank_map_pick` (
 `hero_rank_map_pick_id` BIGINT NOT NULL AUTO_INCREMENT,
  `hero_id` INT NOT NULL,
  `rank_id` INT NOT NULL,
  `map_id` INT NOT NULL,
  `pick_rate` FLOAT NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_rank_map_pick_id`),
  UNIQUE KEY `uq_hero_rank_map_pick_snapshot` (`hero_id`, `rank_id`, `map_id`, `date_of_the_data`),
  CONSTRAINT `fk_hrmp_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`),
  CONSTRAINT `fk_hrmp_rank` FOREIGN KEY (`rank_id`) REFERENCES `rank` (`rank_id`),
  CONSTRAINT `fk_hrmp_map` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`)
) COMMENT='Histórico granular de Pick Rate por Herói/Rank/Mapa';

-- *** NOVAS TABELAS ***
-- Agregação por Herói, Modo de Jogo e Rank
CREATE TABLE `hero_game_mode_rank_win` (
  `hero_game_mode_rank_win_id` INT NOT NULL AUTO_INCREMENT,
  `hero_id` INT NOT NULL,
  `game_mode_id` INT NOT NULL,
  `rank_id` INT NOT NULL,
  `win_rate` FLOAT NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_game_mode_rank_win_id`),
  UNIQUE KEY `uq_hero_gm_rank_win_snapshot` (`hero_id`, `game_mode_id`, `rank_id`, `date_of_the_data`),
  CONSTRAINT `fk_hgrw_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`),
  CONSTRAINT `fk_hgrw_gm` FOREIGN KEY (`game_mode_id`) REFERENCES `game_mode` (`game_mode_id`),
  CONSTRAINT `fk_hgrw_rank` FOREIGN KEY (`rank_id`) REFERENCES `rank` (`rank_id`)
) COMMENT='Histórico de Win Rate agregado por Herói, Modo de Jogo e Rank';

CREATE TABLE `hero_game_mode_rank_pick` (
  `hero_game_mode_rank_pick_id` INT NOT NULL AUTO_INCREMENT,
  `hero_id` INT NOT NULL,
  `game_mode_id` INT NOT NULL,
  `rank_id` INT NOT NULL,
  `pick_rate` FLOAT NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_game_mode_rank_pick_id`),
  UNIQUE KEY `uq_hero_gm_rank_pick_snapshot` (`hero_id`, `game_mode_id`, `rank_id`, `date_of_the_data`),
  CONSTRAINT `fk_hgrp_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`),
  CONSTRAINT `fk_hgrp_gm` FOREIGN KEY (`game_mode_id`) REFERENCES `game_mode` (`game_mode_id`),
  CONSTRAINT `fk_hgrp_rank` FOREIGN KEY (`rank_id`) REFERENCES `rank` (`rank_id`)
) COMMENT='Histórico de Pick Rate agregado por Herói, Modo de Jogo e Rank';

SET FOREIGN_KEY_CHECKS=1;

-- =======================================================================================
-- ETAPA 5: Criação de VIEWS "_latest" para TODAS as Tabelas de Fato
-- =======================================================================================

CREATE OR REPLACE VIEW `vw_hero_win_latest` AS
WITH RankedData AS ( SELECT d.*, ROW_NUMBER() OVER (PARTITION BY d.hero_id ORDER BY d.date_of_the_data DESC) as rn FROM `hero_win` d )
SELECT * FROM RankedData WHERE rn = 1;

CREATE OR REPLACE VIEW `vw_hero_pick_latest` AS
WITH RankedData AS ( SELECT d.*, ROW_NUMBER() OVER (PARTITION BY d.hero_id ORDER BY d.date_of_the_data DESC) as rn FROM `hero_pick` d )
SELECT * FROM RankedData WHERE rn = 1;

CREATE OR REPLACE VIEW `vw_hero_rank_win_latest` AS
WITH RankedData AS ( SELECT d.*, ROW_NUMBER() OVER (PARTITION BY d.hero_id, d.rank_id ORDER BY d.date_of_the_data DESC) as rn FROM `hero_rank_win` d )
SELECT * FROM RankedData WHERE rn = 1;

CREATE OR REPLACE VIEW `vw_hero_rank_pick_latest` AS
WITH RankedData AS ( SELECT d.*, ROW_NUMBER() OVER (PARTITION BY d.hero_id, d.rank_id ORDER BY d.date_of_the_data DESC) as rn FROM `hero_rank_pick` d )
SELECT * FROM RankedData WHERE rn = 1;

CREATE OR REPLACE VIEW `vw_hero_map_win_latest` AS
WITH RankedData AS ( SELECT d.*, ROW_NUMBER() OVER (PARTITION BY d.hero_id, d.map_id ORDER BY d.date_of_the_data DESC) as rn FROM `hero_map_win` d )
SELECT * FROM RankedData WHERE rn = 1;

CREATE OR REPLACE VIEW `vw_hero_map_pick_latest` AS
WITH RankedData AS ( SELECT d.*, ROW_NUMBER() OVER (PARTITION BY d.hero_id, d.map_id ORDER BY d.date_of_the_data DESC) as rn FROM `hero_map_pick` d )
SELECT * FROM RankedData WHERE rn = 1;

CREATE OR REPLACE VIEW `vw_hero_game_mode_win_latest` AS
WITH RankedData AS ( SELECT d.*, ROW_NUMBER() OVER (PARTITION BY d.hero_id, d.game_mode_id ORDER BY d.date_of_the_data DESC) as rn FROM `hero_game_mode_win` d )
SELECT * FROM RankedData WHERE rn = 1;

CREATE OR REPLACE VIEW `vw_hero_game_mode_pick_latest` AS
WITH RankedData AS ( SELECT d.*, ROW_NUMBER() OVER (PARTITION BY d.hero_id, d.game_mode_id ORDER BY d.date_of_the_data DESC) as rn FROM `hero_game_mode_pick` d )
SELECT * FROM RankedData WHERE rn = 1;

CREATE OR REPLACE VIEW `vw_hero_rank_map_win_latest` AS
WITH RankedData AS ( SELECT d.*, ROW_NUMBER() OVER (PARTITION BY d.hero_id, d.rank_id, d.map_id ORDER BY d.date_of_the_data DESC) as rn FROM `hero_rank_map_win` d )
SELECT * FROM RankedData WHERE rn = 1;

CREATE OR REPLACE VIEW `vw_hero_rank_map_pick_latest` AS
WITH RankedData AS ( SELECT d.*, ROW_NUMBER() OVER (PARTITION BY d.hero_id, d.rank_id, d.map_id ORDER BY d.date_of_the_data DESC) as rn FROM `hero_rank_map_pick` d )
SELECT * FROM RankedData WHERE rn = 1;

-- *** NOVAS VIEWS _LATEST ***
CREATE OR REPLACE VIEW `vw_hero_game_mode_rank_win_latest` AS
WITH RankedData AS ( SELECT d.*, ROW_NUMBER() OVER (PARTITION BY d.hero_id, d.game_mode_id, d.rank_id ORDER BY d.date_of_the_data DESC) as rn FROM `hero_game_mode_rank_win` d )
SELECT * FROM RankedData WHERE rn = 1;

CREATE OR REPLACE VIEW `vw_hero_game_mode_rank_pick_latest` AS
WITH RankedData AS ( SELECT d.*, ROW_NUMBER() OVER (PARTITION BY d.hero_id, d.game_mode_id, d.rank_id ORDER BY d.date_of_the_data DESC) as rn FROM `hero_game_mode_rank_pick` d )
SELECT * FROM RankedData WHERE rn = 1;


-- =======================================================================================
-- ETAPA 6: SEED (Dados iniciais para Dimensões)
-- =======================================================================================

INSERT INTO `role` (`role`) VALUES ('DAMAGE'), ('SUPPORT'), ('TANK');

INSERT INTO `rank` (`rank_name`) VALUES
('Bronze'), ('Silver'), ('Gold'), ('Platinum'), ('Diamond'), ('Master'), ('Grandmaster');

INSERT INTO `game_mode` (`game_mode_name`) VALUES
('Control'), ('Escort'), ('Flashpoint'), ('Hybrid'), ('Push');

-- =======================================================================================
-- ETAPA 7: CONFIRMAÇÃO DE CONCLUSÃO
-- =======================================================================================
SELECT 'Banco de dados (v0.6.0) recriado com tabelas de fato separadas (históricas, ID PK + UNIQUE natural), novas tabelas hero_game_mode_rank_* e views _latest dedicadas.' AS status;