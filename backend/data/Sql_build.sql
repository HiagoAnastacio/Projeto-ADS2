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
  `role_id` INT NOT NULL,
  `hero_name` VARCHAR(45) NOT NULL,
  `hero_icon_img_link` VARCHAR(1000) DEFAULT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_id`),
  CONSTRAINT `fk_hero_role` FOREIGN KEY (`role_id`) REFERENCES `role` (`role_id`) ON DELETE CASCADE
);

CREATE TABLE `map` (
  `map_id` INT NOT NULL AUTO_INCREMENT,
  `game_mode_id` INT NOT NULL,
  `map_name` VARCHAR(45) NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`map_id`),
  CONSTRAINT `fk_map_game_mode` FOREIGN KEY (`game_mode_id`) REFERENCES `game_mode` (`game_mode_id`) ON DELETE CASCADE
);

-- Nível 3: Tabelas de Fato (Dados Granulares)
CREATE TABLE `hero_rank_map_win` (
  `hero_rank_map_win_id` INT NOT NULL AUTO_INCREMENT,
  `hero_id` INT NOT NULL,
  `map_id` INT NOT NULL,
  `rank_id` INT NOT NULL,
  `win_rate` DECIMAL(5,2) NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_rank_map_win_id`),
  CONSTRAINT `fk_hrw_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_hrw_map` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_hrw_rank` FOREIGN KEY (`rank_id`) REFERENCES `rank` (`rank_id`) ON DELETE CASCADE
);

CREATE TABLE `hero_rank_map_pick` (
  `hero_rank_map_pick_id` INT NOT NULL AUTO_INCREMENT,
  `hero_id` INT NOT NULL,
  `map_id` INT NOT NULL,
  `rank_id` INT NOT NULL,
  `pick_rate` DECIMAL(5,2) NOT NULL,
  `date_of_the_data` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_rank_map_pick_id`),
  CONSTRAINT `fk_hrp_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_hrp_map` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_hrp_rank` FOREIGN KEY (`rank_id`) REFERENCES `rank` (`rank_id`) ON DELETE CASCADE
);

-- =======================================================================================
-- ETAPA 3: Adicionar Constraints de Unicidade (UNIQUE KEYS)
-- =======================================================================================
ALTER TABLE `role` ADD UNIQUE KEY `role_UNIQUE` (`role`);
ALTER TABLE `rank` ADD UNIQUE KEY `rank_name_UNIQUE` (`rank_name`);
ALTER TABLE `game_mode` ADD UNIQUE KEY `game_mode_name_UNIQUE` (`game_mode_name`);
ALTER TABLE `hero` ADD UNIQUE KEY `hero_name_UNIQUE` (`hero_name`);
ALTER TABLE `map` ADD UNIQUE KEY `map_name_UNIQUE` (`map_name`);

-- Adiciona a chave única composta para as tabelas de fato, essencial para o `ON DUPLICATE KEY UPDATE` funcionar.
ALTER TABLE `hero_rank_map_win` ADD UNIQUE KEY `unique_win_combination` (`hero_id`, `map_id`, `rank_id`);
ALTER TABLE `hero_rank_map_pick` ADD UNIQUE KEY `unique_pick_combination` (`hero_id`, `map_id`, `rank_id`);

-- =======================================================================================
-- ETAPA 4: Inserir Dados Estáticos de Nível 1 (Seed com atualização de timestamp)
-- =======================================================================================
INSERT INTO `role` (`role`) VALUES ('TANK'), ('DAMAGE'), ('SUPPORT')
ON DUPLICATE KEY UPDATE role=VALUES(role), date_of_the_data=CURRENT_TIMESTAMP;

INSERT INTO `rank` (`rank_name`) VALUES ('Bronze'), ('Silver'), ('Gold'), ('Platinum'), ('Diamond'), ('Master'), ('Grandmaster')
ON DUPLICATE KEY UPDATE rank_name=VALUES(rank_name), date_of_the_data=CURRENT_TIMESTAMP;

INSERT INTO `game_mode` (`game_mode_name`) VALUES ('Control'), ('Escort'), ('Flashpoint'), ('Hybrid'), ('Push'), ('Clash'), ('Assault')
ON DUPLICATE KEY UPDATE game_mode_name=VALUES(game_mode_name), date_of_the_data=CURRENT_TIMESTAMP;

-- =======================================================================================
-- ETAPA 5: Criar as Views para os Dados Agregados (com timestamp da última atualização)
-- =======================================================================================
CREATE OR REPLACE VIEW `vw_hero_win` AS SELECT `hero_id`, AVG(`win_rate`) AS `win_rate`, MAX(`date_of_the_data`) as `last_updated` FROM `hero_rank_map_win` GROUP BY `hero_id`;
CREATE OR REPLACE VIEW `vw_hero_pick` AS SELECT `hero_id`, AVG(`pick_rate`) AS `pick_rate`, MAX(`date_of_the_data`) as `last_updated` FROM `hero_rank_map_pick` GROUP BY `hero_id`;
CREATE OR REPLACE VIEW `vw_hero_map_win` AS SELECT `hero_id`, `map_id`, AVG(`win_rate`) AS `win_rate`, MAX(`date_of_the_data`) as `last_updated` FROM `hero_rank_map_win` GROUP BY `hero_id`, `map_id`;
CREATE OR REPLACE VIEW `vw_hero_map_pick` AS SELECT `hero_id`, `map_id`, AVG(`pick_rate`) AS `pick_rate`, MAX(`date_of_the_data`) as `last_updated` FROM `hero_rank_map_pick` GROUP BY `hero_id`, `map_id`;
CREATE OR REPLACE VIEW `vw_hero_rank_win` AS SELECT `hero_id`, `rank_id`, AVG(`win_rate`) AS `win_rate`, MAX(`date_of_the_data`) as `last_updated` FROM `hero_rank_map_win` GROUP BY `hero_id`, `rank_id`;
CREATE OR REPLACE VIEW `vw_hero_rank_pick` AS SELECT `hero_id`, `rank_id`, AVG(`pick_rate`) AS `pick_rate`, MAX(`date_of_the_data`) as `last_updated` FROM `hero_rank_map_pick` GROUP BY `hero_id`, `rank_id`;

-- Reativa a verificação de chaves estrangeiras
SET FOREIGN_KEY_CHECKS=1;

SELECT 'Banco de dados recriado, tabelas, constraints, seeds e views (com suporte temporal) aplicados com sucesso.' AS status;