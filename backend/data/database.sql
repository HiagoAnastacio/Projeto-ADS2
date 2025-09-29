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
  PRIMARY KEY (`game_mode_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `game_mode`
--

LOCK TABLES `game_mode` WRITE;
/*!40000 ALTER TABLE `game_mode` DISABLE KEYS */;
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
  `hero_icon_img_link` varchar(10000) DEFAULT NULL,
  `date_of_the_data` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_id`),
  KEY `fk_hero_role_idx` (`role_id`),
  CONSTRAINT `fk_hero_role` FOREIGN KEY (`role_id`) REFERENCES `role` (`role_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hero`
--

LOCK TABLES `hero` WRITE;
/*!40000 ALTER TABLE `hero` DISABLE KEYS */;
/*!40000 ALTER TABLE `hero` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hero_map_pick`
--

DROP TABLE IF EXISTS `hero_map_pick`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hero_map_pick` (
  `hero_map_pick_id` int NOT NULL AUTO_INCREMENT,
  `hero_id` int NOT NULL,
  `map_id` int NOT NULL,
  `pick_in_map` decimal(4,2) NOT NULL,
  `date_of_the_data` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_map_pick_id`),
  KEY `hero_id` (`hero_id`),
  KEY `map_id` (`map_id`),
  CONSTRAINT `fk_hero_map_pick_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_hero_map_pick_map` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hero_map_pick`
--

LOCK TABLES `hero_map_pick` WRITE;
/*!40000 ALTER TABLE `hero_map_pick` DISABLE KEYS */;
/*!40000 ALTER TABLE `hero_map_pick` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hero_map_win`
--

DROP TABLE IF EXISTS `hero_map_win`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hero_map_win` (
  `hero_map_win_id` int NOT NULL AUTO_INCREMENT,
  `hero_id` int NOT NULL,
  `map_id` int NOT NULL,
  `win_rate` decimal(4,2) NOT NULL,
  `date_of_the_data` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_map_win_id`),
  KEY `hero_id_idx` (`hero_id`),
  KEY `map_id_idx` (`map_id`),
  CONSTRAINT `fk_hero_map_win_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_hero_map_win_map` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hero_map_win`
--

LOCK TABLES `hero_map_win` WRITE;
/*!40000 ALTER TABLE `hero_map_win` DISABLE KEYS */;
/*!40000 ALTER TABLE `hero_map_win` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hero_pick`
--

DROP TABLE IF EXISTS `hero_pick`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hero_pick` (
  `hero_pick_id` int NOT NULL AUTO_INCREMENT,
  `hero_id` int NOT NULL,
  `pick_rate` decimal(4,2) NOT NULL,
  `date_of_the_data` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_pick_id`),
  KEY `hero_id_idx` (`hero_id`),
  CONSTRAINT `fk_hero_pick_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hero_pick`
--

LOCK TABLES `hero_pick` WRITE;
/*!40000 ALTER TABLE `hero_pick` DISABLE KEYS */;
/*!40000 ALTER TABLE `hero_pick` ENABLE KEYS */;
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
  `pick_rate` decimal(4,2) NOT NULL,
  `date_of_the_data` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_rank_map_pick_id`),
  KEY `fk_hero_rank_map_pick_hero_idx` (`hero_id`),
  KEY `fk_hero_rank_map_pick_map_idx` (`map_id`),
  KEY `fk_hero_rank_map_pick_rank_idx` (`rank_id`),
  CONSTRAINT `fk_hero_rank_map_pick_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_hero_rank_map_pick_map` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_hero_rank_map_pick_rank` FOREIGN KEY (`rank_id`) REFERENCES `rank` (`rank_id`) ON DELETE CASCADE
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
  `win_rate` decimal(4,2) NOT NULL,
  `date_of_the_data` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_rank_map_win_id`),
  KEY `fk_hero_rank_map_win_hero_idx` (`hero_id`),
  KEY `fk_hero_rank_map_win_map_idx` (`map_id`),
  KEY `fk_hero_rank_map_win_rank_idx` (`rank_id`),
  CONSTRAINT `fk_hero_rank_map_win_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_hero_rank_map_win_map` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_hero_rank_map_win_rank` FOREIGN KEY (`rank_id`) REFERENCES `rank` (`rank_id`) ON DELETE CASCADE
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
-- Table structure for table `hero_rank_pick`
--

DROP TABLE IF EXISTS `hero_rank_pick`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hero_rank_pick` (
  `hero_rank_pick_id` int NOT NULL AUTO_INCREMENT,
  `hero_id` int NOT NULL,
  `rank_id` int NOT NULL,
  `pick_rate` decimal(4,2) NOT NULL,
  `date_of_the_data` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_rank_pick_id`),
  KEY `fk_hero_rank_pick_hero_idx` (`hero_id`),
  KEY `fk_hero_rank_pick_rank_idx` (`rank_id`),
  CONSTRAINT `fk_hero_rank_pick_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_hero_rank_pick_rank` FOREIGN KEY (`rank_id`) REFERENCES `rank` (`rank_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hero_rank_pick`
--

LOCK TABLES `hero_rank_pick` WRITE;
/*!40000 ALTER TABLE `hero_rank_pick` DISABLE KEYS */;
/*!40000 ALTER TABLE `hero_rank_pick` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hero_rank_win`
--

DROP TABLE IF EXISTS `hero_rank_win`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hero_rank_win` (
  `hero_rank_win_id` int NOT NULL AUTO_INCREMENT,
  `hero_id` int NOT NULL,
  `rank_id` int NOT NULL,
  `win_rate` decimal(4,2) NOT NULL,
  `date_of_the_data` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_rank_win_id`),
  KEY `fk_hero_rank_win_hero_idx` (`hero_id`),
  KEY `fk_hero_rank_win_rank_idx` (`rank_id`),
  CONSTRAINT `fk_hero_rank_win_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_hero_rank_win_rank` FOREIGN KEY (`rank_id`) REFERENCES `rank` (`rank_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hero_rank_win`
--

LOCK TABLES `hero_rank_win` WRITE;
/*!40000 ALTER TABLE `hero_rank_win` DISABLE KEYS */;
/*!40000 ALTER TABLE `hero_rank_win` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hero_win`
--

DROP TABLE IF EXISTS `hero_win`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hero_win` (
  `hero_win_id` int NOT NULL AUTO_INCREMENT,
  `hero_id` int NOT NULL,
  `win_rate` decimal(4,2) NOT NULL,
  `date_of_the_data` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`hero_win_id`),
  KEY `hero_id_idx` (`hero_id`),
  KEY `hero_id` (`hero_id`),
  CONSTRAINT `fk_hero_win_hero` FOREIGN KEY (`hero_id`) REFERENCES `hero` (`hero_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hero_win`
--

LOCK TABLES `hero_win` WRITE;
/*!40000 ALTER TABLE `hero_win` DISABLE KEYS */;
/*!40000 ALTER TABLE `hero_win` ENABLE KEYS */;
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
  KEY `fk_map_game_mode_idx` (`game_mode_id`),
  CONSTRAINT `fk_map_game_mode` FOREIGN KEY (`game_mode_id`) REFERENCES `game_mode` (`game_mode_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
  PRIMARY KEY (`rank_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rank`
--

LOCK TABLES `rank` WRITE;
/*!40000 ALTER TABLE `rank` DISABLE KEYS */;
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
  PRIMARY KEY (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role`
--

LOCK TABLES `role` WRITE;
/*!40000 ALTER TABLE `role` DISABLE KEYS */;
/*!40000 ALTER TABLE `role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'projeto_ads2'
--

--
-- Dumping routines for database 'projeto_ads2'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-29 14:39:28
