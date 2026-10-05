/*
 Navicat Premium Data Transfer

 Source Server         : root
 Source Server Type    : MySQL
 Source Server Version : 80037 (8.0.37)
 Source Host           : localhost:3306
 Source Schema         : my_resume_db

 Target Server Type    : MySQL
 Target Server Version : 80037 (8.0.37)
 File Encoding         : 65001

 Date: 06/05/2026 14:46:22
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for product
-- ----------------------------
DROP TABLE IF EXISTS `product`;
CREATE TABLE `product`  (
  `product_id` int NOT NULL AUTO_INCREMENT,
  `product_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `price` decimal(10, 2) NOT NULL,
  `category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`product_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 11 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of product
-- ----------------------------
INSERT INTO `product` VALUES (1, '无线蓝牙耳机', 199.00, '数码');
INSERT INTO `product` VALUES (2, '智能手表', 599.00, '数码');
INSERT INTO `product` VALUES (3, '纯棉T恤', 59.00, '服饰');
INSERT INTO `product` VALUES (4, '牛仔裤', 129.00, '服饰');
INSERT INTO `product` VALUES (5, '保温杯', 89.00, '家居');
INSERT INTO `product` VALUES (6, '加湿器', 159.00, '家居');
INSERT INTO `product` VALUES (7, '机械键盘', 299.00, '数码');
INSERT INTO `product` VALUES (8, '办公椅', 399.00, '家具');
INSERT INTO `product` VALUES (9, '防晒霜', 79.00, '美妆');
INSERT INTO `product` VALUES (10, '洗面奶', 49.00, '美妆');

SET FOREIGN_KEY_CHECKS = 1;
