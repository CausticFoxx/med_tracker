-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema med_tracker
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema med_tracker
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `med_tracker` DEFAULT CHARACTER SET utf8 ;
USE `med_tracker` ;

-- -----------------------------------------------------
-- Table `med_tracker`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `med_tracker`.`users` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(255) NOT NULL,
  `last_name` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 4
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `med_tracker`.`medications`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `med_tracker`.`medications` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `user_id` INT(11) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `fk_medications_users_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_medications_users`
    FOREIGN KEY (`user_id`)
    REFERENCES `med_tracker`.`users` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `med_tracker`.`medication_events`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `med_tracker`.`medication_events` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `user_id` INT(11) NOT NULL,
  `medication_id` INT(11) NOT NULL,
  `administered_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `dose` INT(11) NOT NULL,
  `dose_units` ENUM('Milligrams (mg)', 'Micrograms (mcg)', 'Grams (g)', 'Milliliters (ml)', 'Teaspoon (tsp)', 'Tablespoon (Tbsp)', 'International Units (IU)', 'Other') NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `fk_medication events_users1_idx` (`user_id` ASC) VISIBLE,
  INDEX `fk_medication events_medications1_idx` (`medication_id` ASC) VISIBLE,
  CONSTRAINT `fk_medication events_medications1`
    FOREIGN KEY (`medication_id`)
    REFERENCES `med_tracker`.`medications` (`id`),
  CONSTRAINT `fk_medication events_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `med_tracker`.`users` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
