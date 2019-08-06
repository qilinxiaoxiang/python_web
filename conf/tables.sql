CREATE TABLE `table_1` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'PK',
  `data1` int(11) NOT NULL COMMENT 'data 1',
  `data2` int(11) NOT NULL COMMENT 'data 2',
  `data3` int(11) NOT NULL COMMENT 'data 3',
  `data4` int(11) NOT NULL COMMENT 'data 4',
  `flag` int(11) NOT NULL DEFAULT 0 COMMENT '0-normal, 1-important',
  `created_time` datetime NOT NULL COMMENT 'created_time',
  PRIMARY KEY (`id`),
  KEY `created_time` (`created_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT="table 1";

CREATE TABLE `table_2` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'PK',
  `original_id` int(11) NOT NULL COMMENT 'original id in table 1',
  `data1` int(11) NOT NULL COMMENT 'data 1',
  `data2` int(11) NOT NULL COMMENT 'data 2',
  `data3` int(11) NOT NULL COMMENT 'data 3',
  `data4` int(11) NOT NULL COMMENT 'data 4',
  `flag` int(11) NOT NULL DEFAULT 0 COMMENT '0-normal, 1-important',
  `original_created_time` datetime NOT NULL COMMENT 'created_time in table 1',
  `created_time` datetime NOT NULL COMMENT 'created_time',
  PRIMARY KEY (`id`),
  KEY `created_time` (`created_time`),
  KEY `original_id` (`original_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT="table 2";