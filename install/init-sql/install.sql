/*
 Navicat Premium Data Transfer

 Source Server         : Yearning
 Source Server Type    : MySQL
 Source Server Version : 50721
 Source Host           : 127.0.0.1:3306
 Source Schema         : Yearning

 Target Server Type    : MySQL
 Target Server Version : 50721
 File Encoding         : 65001

 Date: 12/09/2018 17:30:24
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

use Yearning;

BEGIN;
	INSERT INTO `core_grained`(id,username,permissions,updatetime) VALUES (1, 'admin', '{\'ddl\': \'0\', \'ddlcon\': [], \'dml\': \'0\', \'dmlcon\': [], \'dic\': \'0\', \'diccon\': [], \'dicedit\': \'0\', \'user\': \'1\', \'base\': \'1\', \'dicexport\': \'0\', \'person\': [], \'query\': \'0\', \'querycon\': []}',NOW());

	INSERT INTO `core_globalpermissions`(id,authorization,inception,ldap,message,other,updatetime) VALUES (1, 'global', '{\'host\': \'\', \'port\': \'\', \'user\': \'\', \'password\': \'\', \'back_host\': \'\', \'back_port\': \'\', \'back_user\': \'\', \'back_password\': \'\'}', '{\'type\': \'1\', \'host\': \'\', \'sc\': \'\', \'domain\': \'\', \'user\': \'\', \'password\': \'\'}', '{\'webhook\': \'\', \'smtp_host\': \'\', \'smtp_port\': \'\', \'user\': \'\', \'password\': \'\', \'to_user\': \'\', \'mail\': False, \'ding\': False, \'ssl\': False}', '{\'limit\': \'\', \'con_room\': [\'AWS\', \'Aliyun\', \'Own\', \'Other\'], \'foce\': \'\', \'multi\': False, \'query\': False, \'sensitive_list\': [], \'sensitive\': \'\', \'exclued_db_list\': [], \'exclued_db\': \'\', \'email_suffix_list\': [], \'email_suffix\': \'\'}', NOW());

	INSERT INTO `core_account`(id,`password`,is_superuser, username,first_name,last_name,email, is_staff,is_active,`group`,department,auth_group,from_ldap,date_joined,updatetime) VALUES (1,'pbkdf2_sha256$100000$Dy6mFniGxTZa$YBQ9cX0iPQvTYp06C5ZiVgXICTHNTiwWhWYnRmcqjHY=',0, 'admin','admin','admin','', 1, 1, 'admin','dba','admin',0,NOW(), NOW());
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
