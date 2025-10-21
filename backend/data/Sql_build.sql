-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema projeto_ads2
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `projeto_ads2` ;

-- -----------------------------------------------------
-- Schema projeto_ads2
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `projeto_ads2` DEFAULT CHARACTER SET utf8 ;
USE `projeto_ads2` ;

-- Desativa a verificação de chaves estrangeiras durante a criação
SET FOREIGN_KEY_CHECKS=0;

-- -----------------------------------------------------
-- Table `projeto_ads2`.`role`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `projeto_ads2`.`role` (
  `role_id` INT NOT NULL AUTO_INCREMENT,
  `role` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`role_id`),
  UNIQUE INDEX `role_UNIQUE` (`role` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `projeto_ads2`.`hero`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `projeto_ads2`.`hero` (
  `hero_id` INT NOT NULL AUTO_INCREMENT,
  `hero_name` VARCHAR(45) NOT NULL,
  `role_id` INT NOT NULL,
  `hero_icon_img_link` VARCHAR(255) NULL,
  PRIMARY KEY (`hero_id`),
  UNIQUE INDEX `hero_name_UNIQUE` (`hero_name` ASC) VISIBLE,
  INDEX `fk_hero_role1_idx` (`role_id` ASC) VISIBLE,
  CONSTRAINT `fk_hero_role1`
    FOREIGN KEY (`role_id`)
    REFERENCES `projeto_ads2`.`role` (`role_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `projeto_ads2`.`rank`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `projeto_ads2`.`rank` (
  `rank_id` INT NOT NULL AUTO_INCREMENT,
  `rank_name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`rank_id`),
  UNIQUE INDEX `rank_name_UNIQUE` (`rank_name` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `projeto_ads2`.`game_mode`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `projeto_ads2`.`game_mode` (
  `game_mode_id` INT NOT NULL AUTO_INCREMENT,
  `game_mode_name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`game_mode_id`),
  UNIQUE INDEX `game_mode_name_UNIQUE` (`game_mode_name` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `projeto_ads2`.`map`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `projeto_ads2`.`map` (
  `map_id` INT NOT NULL AUTO_INCREMENT,
  `map_name` VARCHAR(45) NOT NULL,
  `game_mode_id` INT NOT NULL,
  PRIMARY KEY (`map_id`),
  INDEX `fk_map_game_mode1_idx` (`game_mode_id` ASC) VISIBLE,
  UNIQUE INDEX `map_name_UNIQUE` (`map_name` ASC) VISIBLE,
  CONSTRAINT `fk_map_game_mode1`
    FOREIGN KEY (`game_mode_id`)
    REFERENCES `projeto_ads2`.`game_mode` (`game_mode_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `projeto_ads2`.`hero_rank_map_win`
-- (ALTERAÇÃO: Esta é agora uma tabela de "log histórico")
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `projeto_ads2`.`hero_rank_map_win` (
  `hero_rank_map_win_id` INT NOT NULL AUTO_INCREMENT,
  `hero_id` INT NOT NULL,
  `rank_id` INT NOT NULL,
  `map_id` INT NOT NULL,
  `win_rate` FLOAT NOT NULL,
  `date_of_the_data` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_rank_map_win_id`), -- <-- ALTERAÇÃO: Chave primária simples
  -- ALTERAÇÃO: 'UNIQUE INDEX' removido para permitir o histórico
  INDEX `fk_hero_has_rank_rank2_idx` (`rank_id` ASC) VISIBLE,
  INDEX `fk_hero_has_rank_hero2_idx` (`hero_id` ASC) VISIBLE,
  INDEX `fk_hero_rank_win_map1_idx` (`map_id` ASC) VISIBLE,
  -- ALTERAÇÃO: Adicionado índice para performance de consulta
  INDEX `idx_query` (`hero_id` ASC, `rank_id` ASC, `map_id` ASC, `date_of_the_data` DESC),
  CONSTRAINT `fk_hero_has_rank_hero2`
    FOREIGN KEY (`hero_id`)
    REFERENCES `projeto_ads2`.`hero` (`hero_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_hero_has_rank_rank2`
    FOREIGN KEY (`rank_id`)
    REFERENCES `projeto_ads2`.`rank` (`rank_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_hero_rank_win_map1`
    FOREIGN KEY (`map_id`)
    REFERENCES `projeto_ads2`.`map` (`map_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `projeto_ads2`.`hero_rank_map_pick`
-- (ALTERAÇÃO: Esta é agora uma tabela de "log histórico")
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `projeto_ads2`.`hero_rank_map_pick` (
  `hero_rank_map_pick_id` INT NOT NULL AUTO_INCREMENT,
  `hero_id` INT NOT NULL,
  `rank_id` INT NOT NULL,
  `map_id` INT NOT NULL,
  `pick_rate` FLOAT NOT NULL,
  `date_of_the_data` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_rank_map_pick_id`), -- <-- ALTERAÇÃO: Chave primária simples
  -- ALTERAÇÃO: 'UNIQUE INDEX' removido para permitir o histórico
  INDEX `fk_hero_has_rank_rank3_idx` (`rank_id` ASC) VISIBLE,
  INDEX `fk_hero_has_rank_hero3_idx` (`hero_id` ASC) VISIBLE,
  INDEX `fk_hero_rank_pick_map1_idx` (`map_id` ASC) VISIBLE,
  -- ALTERAÇÃO: Adicionado índice para performance de consulta
  INDEX `idx_query` (`hero_id` ASC, `rank_id` ASC, `map_id` ASC, `date_of_the_data` DESC),
  CONSTRAINT `fk_hero_has_rank_hero3`
    FOREIGN KEY (`hero_id`)
    REFERENCES `projeto_ads2`.`hero` (`hero_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_hero_has_rank_rank3`
    FOREIGN KEY (`rank_id`)
    REFERENCES `projeto_ads2`.`rank` (`rank_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_hero_rank_pick_map1`
    FOREIGN KEY (`map_id`)
    REFERENCES `projeto_ads2`.`map` (`map_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- -----------------------------------------------------
-- Views de Snapshot (Novas Views Base)
-- -----------------------------------------------------

-- ALTERAÇÃO: Nova View de "snapshot" para 'win_rate'
CREATE OR REPLACE VIEW `vw_snapshot_hero_rank_map_win` AS
WITH RankedStats AS (
    SELECT
        *,
        ROW_NUMBER() OVER(
            PARTITION BY `hero_id`, `rank_id`, `map_id`
            ORDER BY `date_of_the_data` DESC
        ) as rn
    FROM
        `hero_rank_map_win`
)
SELECT
    `hero_rank_map_win_id`,
    `hero_id`,
    `rank_id`,
    `map_id`,
    `win_rate`,
    `date_of_the_data`
FROM
    RankedStats
WHERE
    rn = 1;

-- ALTERAÇÃO: Nova View de "snapshot" para 'pick_rate'
CREATE OR REPLACE VIEW `vw_snapshot_hero_rank_map_pick` AS
WITH RankedStats AS (
    SELECT
        *,
        ROW_NUMBER() OVER(
            PARTITION BY `hero_id`, `rank_id`, `map_id`
            ORDER BY `date_of_the_data` DESC
        ) as rn
    FROM
        `hero_rank_map_pick`
)
SELECT
    `hero_rank_map_pick_id`,
    `hero_id`,
    `rank_id`,
    `map_id`,
    `pick_rate`,
    `date_of_the_data`
FROM
    RankedStats
WHERE
    rn = 1;


-- -----------------------------------------------------
-- Views Agregadas (Refatoradas para usar os Snapshots)
-- -----------------------------------------------------

-- -----------------------------------------------------
-- View `projeto_ads2`.`vw_hero_win`
-- (ALTERAÇÃO: Agora lê da View de snapshot)
-- -----------------------------------------------------
CREATE OR REPLACE VIEW `vw_hero_win` AS
    SELECT 
        `h`.`hero_id` AS `hero_id`,
        `h`.`hero_name` AS `hero_name`,
        `h`.`hero_icon_img_link` AS `hero_icon_img_link`,
        AVG(`f`.`win_rate`) AS `avg_win_rate`,
        MAX(`f`.`date_of_the_data`) AS `last_updated`
    FROM
        (`vw_snapshot_hero_rank_map_win` `f` -- <-- ALTERAÇÃO
        JOIN `hero` `h` ON ((`f`.`hero_id` = `h`.`hero_id`)))
    GROUP BY `h`.`hero_id`;

-- -----------------------------------------------------
-- View `projeto_ads2`.`vw_hero_pick`
-- (ALTERAÇÃO: Agora lê da View de snapshot)
-- -----------------------------------------------------
CREATE OR REPLACE VIEW `vw_hero_pick` AS
    SELECT 
        `h`.`hero_id` AS `hero_id`,
        `h`.`hero_name` AS `hero_name`,
        `h`.`hero_icon_img_link` AS `hero_icon_img_link`,
        AVG(`f`.`pick_rate`) AS `avg_pick_rate`,
        MAX(`f`.`date_of_the_data`) AS `last_updated`
    FROM
        (`vw_snapshot_hero_rank_map_pick` `f` -- <-- ALTERAÇÃO
        JOIN `hero` `h` ON ((`f`.`hero_id` = `h`.`hero_id`)))
    GROUP BY `h`.`hero_id`;

-- -----------------------------------------------------
-- View `projeto_ads2`.`vw_hero_map_win`
-- (ALTERAÇÃO: Agora lê da View de snapshot)
-- -----------------------------------------------------
CREATE OR REPLACE VIEW `vw_hero_map_win` AS
    SELECT 
        `h`.`hero_id` AS `hero_id`,
        `h`.`hero_name` AS `hero_name`,
        `m`.`map_id` AS `map_id`,
        `m`.`map_name` AS `map_name`,
        AVG(`f`.`win_rate`) AS `avg_win_rate`,
        MAX(`f`.`date_of_the_data`) AS `last_updated`
    FROM
        ((`vw_snapshot_hero_rank_map_win` `f` -- <-- ALTERAÇÃO
        JOIN `hero` `h` ON ((`f`.`hero_id` = `h`.`hero_id`)))
        JOIN `map` `m` ON ((`f`.`map_id` = `m`.`map_id`)))
    GROUP BY `h`.`hero_id` , `m`.`map_id`;

-- -----------------------------------------------------
-- View `projeto_ads2`.`vw_hero_map_pick`
-- (ALTERAÇÃO: Agora lê da View de snapshot)
-- -----------------------------------------------------
CREATE OR REPLACE VIEW `vw_hero_map_pick` AS
    SELECT 
        `h`.`hero_id` AS `hero_id`,
        `h`.`hero_name` AS `hero_name`,
        `m`.`map_id` AS `map_id`,
        `m`.`map_name` AS `map_name`,
        AVG(`f`.`pick_rate`) AS `avg_pick_rate`,
        MAX(`f`.`date_of_the_data`) AS `last_updated`
    FROM
        ((`vw_snapshot_hero_rank_map_pick` `f` -- <-- ALTERAÇÃO
        JOIN `hero` `h` ON ((`f`.`hero_id = h`.`hero_id`)))
        JOIN `map` `m` ON ((`f`.`map_id` = `m`.`map_id`)))
    GROUP BY `h`.`hero_id` , `m`.`map_id`;

-- -----------------------------------------------------
-- View `projeto_ads2`.`vw_hero_rank_win`
-- (ALTERAÇÃO: Agora lê da View de snapshot)
-- -----------------------------------------------------
CREATE OR REPLACE VIEW `vw_hero_rank_win` AS
    SELECT 
        `h`.`hero_id` AS `hero_id`,
        `h`.`hero_name` AS `hero_name`,
        `r`.`rank_id` AS `rank_id`,
        `r`.`rank_name` AS `rank_name`,
        AVG(`f`.`win_rate`) AS `avg_win_rate`,
        MAX(`f`.`date_of_the_data`) AS `last_updated`
    FROM
        ((`vw_snapshot_hero_rank_map_win` `f` -- <-- ALTERAÇÃO
        JOIN `hero` `h` ON ((`f`.`hero_id` = `h`.`hero_id`)))
        JOIN `rank` `r` ON ((`f`.`rank_id` = `r`.`rank_id`)))
    GROUP BY `h`.`hero_id` , `r`.`rank_id`;

-- -----------------------------------------------------
-- View `projeto_ads2`.`vw_hero_rank_pick`
-- (ALTERAÇÃO: Agora lê da View de snapshot)
-- -----------------------------------------------------
CREATE OR REPLACE VIEW `vw_hero_rank_pick` AS
    SELECT 
        `h`.`hero_id` AS `hero_id`,
        `h`.`hero_name` AS `hero_name`,
        `r`.`rank_id` AS `rank_id`,
        `r`.`rank_name` AS `rank_name`,
        AVG(`f`.`pick_rate`) AS `avg_pick_rate`,
        MAX(`f`.`date_of_the_data`) AS `last_updated`
    FROM
        ((`vw_snapshot_hero_rank_map_pick` `f` -- <-- ALTERAÇÃO
        JOIN `hero` `h` ON ((`f`.`hero_id` = `h`.`hero_id`)))
        JOIN `rank` `r` ON ((`f`.`rank_id` = `r`.`rank_id`)))
    GROUP BY `h`.`hero_id` , `r`.`rank_id`;

-- -----------------------------------------------------
-- DADOS INICIAIS (SEED)
-- -----------------------------------------------------
-- -----------------------------------------------------
-- DADOS INICIAIS (SEED)
-- -----------------------------------------------------
-- ALTERAÇÃO: Corrigida a capitalização de Tank, Damage, Support
INSERT INTO `role` (`role`) VALUES ('Tank'), ('Damage'), ('Support');
INSERT INTO `rank` (`rank_name`) VALUES ('bronze'), ('silver'), ('gold'), ('platinum'), ('diamond'), ('master'), ('grandmaster');
INSERT INTO `game_mode` (`game_mode_name`) VALUES ('Control'), ('Escort'), ('Flashpoint'), ('Hybrid'), ('Push'), ('Clash');