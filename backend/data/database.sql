CREATE DATABASE  IF NOT EXISTS `projeto_ads2` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `projeto_ads2`;
-- MySQL dump 10.13  Distrib 8.0.34, for Win64 (x86_64)
--
-- Host: localhost    Database: projeto_ads2
-- ------------------------------------------------------
-- Server version	8.0.35

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `game_mode`
--

DROP TABLE IF EXISTS `game_mode`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `game_mode` (
  `game_mode_id` int NOT NULL AUTO_INCREMENT,
  `game_mode_name` varchar(45) NOT NULL,
  `date_of_the_data` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`game_mode_id`),
  UNIQUE KEY `game_mode_name_UNIQUE` (`game_mode_name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `game_mode`
--

LOCK TABLES `game_mode` WRITE;
/*!40000 ALTER TABLE `game_mode` DISABLE KEYS */;
INSERT INTO `game_mode` VALUES (1,'Control','2025-10-14 10:50:19'),(2,'Escort','2025-10-14 10:50:19'),(3,'Flashpoint','2025-10-14 10:50:19'),(4,'Hybrid','2025-10-14 10:50:19'),(5,'Push','2025-10-14 10:50:19'),(6,'Clash','2025-10-14 10:50:19'),(7,'Assault','2025-10-14 10:50:19');
/*!40000 ALTER TABLE `game_mode` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hero`
--

DROP TABLE IF EXISTS `hero`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hero` (
  `hero_id` int NOT NULL AUTO_INCREMENT,
  `role_id` int NOT NULL,
  `hero_name` varchar(45) NOT NULL,
  `hero_icon_img_link` varchar(1000) DEFAULT NULL,
  `date_of_the_data` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_id`),
  UNIQUE KEY `hero_name_UNIQUE` (`hero_name`),
  KEY `fk_hero_role` (`role_id`),
  CONSTRAINT `fk_hero_role` FOREIGN KEY (`role_id`) REFERENCES `role` (`role_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hero`
--

LOCK TABLES `hero` WRITE;
/*!40000 ALTER TABLE `hero` DISABLE KEYS */;
/*!40000 ALTER TABLE `hero` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hero_rank_map_pick`
--

DROP TABLE IF EXISTS `hero_rank_map_pick`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hero_rank_map_pick` (
  `hero_rank_map_pick_id` int NOT NULL AUTO_INCREMENT,
  `hero_id` int NOT NULL,
  `map_id` int NOT NULL,
  `rank_id` int NOT NULL,
  `pick_rate` decimal(5,2) NOT NULL,
  `date_of_the_data` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_rank_map_pick_id`),
  UNIQUE KEY `unique_pick_combination` (`hero_id`,`map_id`,`rank_id`),
  KEY `fk_hrp_map` (`map_id`),
  KEY `fk_hrp_rank` (`rank_id`),
  CONSTRAINT `fk_hrp_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_hrp_map` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_hrp_rank` FOREIGN KEY (`rank_id`) REFERENCES `rank` (`rank_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hero_rank_map_pick`
--

LOCK TABLES `hero_rank_map_pick` WRITE;
/*!40000 ALTER TABLE `hero_rank_map_pick` DISABLE KEYS */;
/*!40000 ALTER TABLE `hero_rank_map_pick` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hero_rank_map_win`
--

DROP TABLE IF EXISTS `hero_rank_map_win`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hero_rank_map_win` (
  `hero_rank_map_win_id` int NOT NULL AUTO_INCREMENT,
  `hero_id` int NOT NULL,
  `map_id` int NOT NULL,
  `rank_id` int NOT NULL,
  `win_rate` decimal(5,2) NOT NULL,
  `date_of_the_data` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_rank_map_win_id`),
  UNIQUE KEY `unique_win_combination` (`hero_id`,`map_id`,`rank_id`),
  KEY `fk_hrw_map` (`map_id`),
  KEY `fk_hrw_rank` (`rank_id`),
  CONSTRAINT `fk_hrw_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_hrw_map` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_hrw_rank` FOREIGN KEY (`rank_id`) REFERENCES `rank` (`rank_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hero_rank_map_win`
--

LOCK TABLES `hero_rank_map_win` WRITE;
/*!40000 ALTER TABLE `hero_rank_map_win` DISABLE KEYS */;
/*!40000 ALTER TABLE `hero_rank_map_win` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `map`
--

DROP TABLE IF EXISTS `map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `map` (
  `map_id` int NOT NULL AUTO_INCREMENT,
  `game_mode_id` int NOT NULL,
  `map_name` varchar(45) NOT NULL,
  `date_of_the_data` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`map_id`),
  UNIQUE KEY `map_name_UNIQUE` (`map_name`),
  KEY `fk_map_game_mode` (`game_mode_id`),
  CONSTRAINT `fk_map_game_mode` FOREIGN KEY (`game_mode_id`) REFERENCES `game_mode` (`game_mode_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `map`
--

LOCK TABLES `map` WRITE;
/*!40000 ALTER TABLE `map` DISABLE KEYS */;
/*!40000 ALTER TABLE `map` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rank`
--

DROP TABLE IF EXISTS `rank`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rank` (
  `rank_id` int NOT NULL AUTO_INCREMENT,
  `rank_name` varchar(45) NOT NULL,
  `date_of_the_data` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`rank_id`),
  UNIQUE KEY `rank_name_UNIQUE` (`rank_name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rank`
--

LOCK TABLES `rank` WRITE;
/*!40000 ALTER TABLE `rank` DISABLE KEYS */;
INSERT INTO `rank` VALUES (1,'Bronze','2025-10-14 10:50:19'),(2,'Silver','2025-10-14 10:50:19'),(3,'Gold','2025-10-14 10:50:19'),(4,'Platinum','2025-10-14 10:50:19'),(5,'Diamond','2025-10-14 10:50:19'),(6,'Master','2025-10-14 10:50:19'),(7,'Grandmaster','2025-10-14 10:50:19');
/*!40000 ALTER TABLE `rank` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role`
--

DROP TABLE IF EXISTS `role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `role` (
  `role_id` int NOT NULL AUTO_INCREMENT,
  `role` varchar(40) NOT NULL,
  `date_of_the_data` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`role_id`),
  UNIQUE KEY `role_UNIQUE` (`role`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role`
--

LOCK TABLES `role` WRITE;
/*!40000 ALTER TABLE `role` DISABLE KEYS */;
INSERT INTO `role` VALUES (1,'TANK','2025-10-14 10:50:18'),(2,'DAMAGE','2025-10-14 10:50:18'),(3,'SUPPORT','2025-10-14 10:50:18');
/*!40000 ALTER TABLE `role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `vw_hero_map_pick`
--

DROP TABLE IF EXISTS `vw_hero_map_pick`;
/*!50001 DROP VIEW IF EXISTS `vw_hero_map_pick`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_hero_map_pick` AS SELECT 
 1 AS `hero_id`,
 1 AS `map_id`,
 1 AS `pick_rate`,
 1 AS `last_updated`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_hero_map_win`
--

DROP TABLE IF EXISTS `vw_hero_map_win`;
/*!50001 DROP VIEW IF EXISTS `vw_hero_map_win`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_hero_map_win` AS SELECT 
 1 AS `hero_id`,
 1 AS `map_id`,
 1 AS `win_rate`,
 1 AS `last_updated`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_hero_pick`
--

DROP TABLE IF EXISTS `vw_hero_pick`;
/*!50001 DROP VIEW IF EXISTS `vw_hero_pick`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_hero_pick` AS SELECT 
 1 AS `hero_id`,
 1 AS `pick_rate`,
 1 AS `last_updated`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_hero_rank_pick`
--

DROP TABLE IF EXISTS `vw_hero_rank_pick`;
/*!50001 DROP VIEW IF EXISTS `vw_hero_rank_pick`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_hero_rank_pick` AS SELECT 
 1 AS `hero_id`,
 1 AS `rank_id`,
 1 AS `pick_rate`,
 1 AS `last_updated`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_hero_rank_win`
--

DROP TABLE IF EXISTS `vw_hero_rank_win`;
/*!50001 DROP VIEW IF EXISTS `vw_hero_rank_win`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_hero_rank_win` AS SELECT 
 1 AS `hero_id`,
 1 AS `rank_id`,
 1 AS `win_rate`,
 1 AS `last_updated`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_hero_win`
--

DROP TABLE IF EXISTS `vw_hero_win`;
/*!50001 DROP VIEW IF EXISTS `vw_hero_win`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_hero_win` AS SELECT 
 1 AS `hero_id`,
 1 AS `win_rate`,
 1 AS `last_updated`*/;
SET character_set_client = @saved_cs_client;

--
-- Dumping events for database 'projeto_ads2'
--

--
-- Dumping routines for database 'projeto_ads2'
--

--
-- Final view structure for view `vw_hero_map_pick`
--

/*!50001 DROP VIEW IF EXISTS `vw_hero_map_pick`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_hero_map_pick` AS select `hero_rank_map_pick`.`hero_id` AS `hero_id`,`hero_rank_map_pick`.`map_id` AS `map_id`,avg(`hero_rank_map_pick`.`pick_rate`) AS `pick_rate`,max(`hero_rank_map_pick`.`date_of_the_data`) AS `last_updated` from `hero_rank_map_pick` group by `hero_rank_map_pick`.`hero_id`,`hero_rank_map_pick`.`map_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_hero_map_win`
--

/*!50001 DROP VIEW IF EXISTS `vw_hero_map_win`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_hero_map_win` AS select `hero_rank_map_win`.`hero_id` AS `hero_id`,`hero_rank_map_win`.`map_id` AS `map_id`,avg(`hero_rank_map_win`.`win_rate`) AS `win_rate`,max(`hero_rank_map_win`.`date_of_the_data`) AS `last_updated` from `hero_rank_map_win` group by `hero_rank_map_win`.`hero_id`,`hero_rank_map_win`.`map_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_hero_pick`
--

/*!50001 DROP VIEW IF EXISTS `vw_hero_pick`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_hero_pick` AS select `hero_rank_map_pick`.`hero_id` AS `hero_id`,avg(`hero_rank_map_pick`.`pick_rate`) AS `pick_rate`,max(`hero_rank_map_pick`.`date_of_the_data`) AS `last_updated` from `hero_rank_map_pick` group by `hero_rank_map_pick`.`hero_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_hero_rank_pick`
--

/*!50001 DROP VIEW IF EXISTS `vw_hero_rank_pick`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_hero_rank_pick` AS select `hero_rank_map_pick`.`hero_id` AS `hero_id`,`hero_rank_map_pick`.`rank_id` AS `rank_id`,avg(`hero_rank_map_pick`.`pick_rate`) AS `pick_rate`,max(`hero_rank_map_pick`.`date_of_the_data`) AS `last_updated` from `hero_rank_map_pick` group by `hero_rank_map_pick`.`hero_id`,`hero_rank_map_pick`.`rank_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_hero_rank_win`
--

/*!50001 DROP VIEW IF EXISTS `vw_hero_rank_win`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_hero_rank_win` AS select `hero_rank_map_win`.`hero_id` AS `hero_id`,`hero_rank_map_win`.`rank_id` AS `rank_id`,avg(`hero_rank_map_win`.`win_rate`) AS `win_rate`,max(`hero_rank_map_win`.`date_of_the_data`) AS `last_updated` from `hero_rank_map_win` group by `hero_rank_map_win`.`hero_id`,`hero_rank_map_win`.`rank_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_hero_win`
--

/*!50001 DROP VIEW IF EXISTS `vw_hero_win`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_hero_win` AS select `hero_rank_map_win`.`hero_id` AS `hero_id`,avg(`hero_rank_map_win`.`win_rate`) AS `win_rate`,max(`hero_rank_map_win`.`date_of_the_data`) AS `last_updated` from `hero_rank_map_win` group by `hero_rank_map_win`.`hero_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-14 10:52:15
