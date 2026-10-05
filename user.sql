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

 Date: 06/05/2026 14:46:28
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 11 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO `user` VALUES (1, '张三', '13800138001', 'zhangsan@test.com', '2026-04-23 16:40:13');
INSERT INTO `user` VALUES (2, '李四', '13800138002', 'lisi@test.com', '2026-04-23 16:40:13');
INSERT INTO `user` VALUES (3, '王五', '13800138003', 'wangwu@test.com', '2026-04-23 16:40:13');
INSERT INTO `user` VALUES (4, '赵六', '13800138004', 'zhaoliu@test.com', '2026-04-23 16:40:13');
INSERT INTO `user` VALUES (5, '陈七', '13800138005', 'chenqi@test.com', '2026-04-23 16:40:13');
INSERT INTO `user` VALUES (6, '刘八', '13800138006', 'liuba@test.com', '2026-04-23 16:40:13');
INSERT INTO `user` VALUES (7, '周九', '13800138007', 'zhoujiu@test.com', '2026-04-23 16:40:13');
INSERT INTO `user` VALUES (8, '吴十', '13800138008', 'wushi@test.com', '2026-04-23 16:40:13');
INSERT INTO `user` VALUES (9, '郑十一', '13800138009', 'zhengshiyi@test.com', '2026-04-23 16:40:13');
INSERT INTO `user` VALUES (10, '钱十二', '13800138010', 'qianshier@test.com', '2026-04-23 16:40:13');

SET FOREIGN_KEY_CHECKS = 1;
