#!/bin/bash

#This script creates the mysql database we need from scratch and sets up a user to access it.
#It is safe to run this if things are already set up.  No worries.

sudo mysql -uroot -B <<"MYEOF"
  CREATE USER IF NOT EXISTS `andromodon`@`localhost` IDENTIFIED BY 'worivrinVosk';
  CREATE DATABASE IF NOT EXISTS `snoutScan` /*!40100 DEFAULT CHARACTER SET utf8 */;
  GRANT ALL ON `snoutScan`.* TO `andromodon`@`localhost`;
MYEOF
