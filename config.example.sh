#!/bin/bash

# 基础路径配置
BASE_DIR="/path/to/report/directory"
SCRIPT_DIR="/path/to/scripts"
LOG_DIR="$SCRIPT_DIR/logs"
TEMP_DIR="$SCRIPT_DIR/temp"

# CSV 文件相关配置
CSV_ENCODING="utf-16le"
CSV_DELIMITER="\t"

# 保留文件策略
# 设置优先保留文件的目录路径
PRESERVE_PATH="/volume3/homes/"
