#!/bin/bash

# 加载配置文件
SCRIPT_PATH=$(dirname $(realpath $0))
source "${SCRIPT_PATH}/../config.sh"

# 记录日志的函数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# 创建所需目录
mkdir -p "$LOG_DIR"
mkdir -p "$TEMP_DIR"

# 获取当前时间戳用于日志文件
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="$LOG_DIR/duplicate_process_$TIMESTAMP.log"

log "开始处理重复文件"

# 获取最新的日期文件夹
LATEST_DIR=$(ls -t "$BASE_DIR" | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}-[0-9]{2}-[0-9]{2}$' | head -n 1)

if [ -z "$LATEST_DIR" ]; then
    log "没有找到符合日期格式的文件夹"
    exit 1
fi

# 构建完整路径
ZIP_FILE="$BASE_DIR/$LATEST_DIR/csv/duplicate_file.csv.zip"
if [ ! -f "$ZIP_FILE" ]; then
    log "未找到ZIP文件: $ZIP_FILE"
    exit 1
fi

# 切换到脚本目录
cd "$SCRIPT_DIR"

# 解压缩文件
log "解压文件: $ZIP_FILE"
7z x -y "$ZIP_FILE"

if [ ! -f "duplicate_file.csv" ]; then
    log "解压后未找到CSV文件"
    exit 1
fi

# 重命名CSV文件（添加日期信息）
NEW_CSV_NAME="duplicate_file_${LATEST_DIR}.csv"
mv "duplicate_file.csv" "$NEW_CSV_NAME"
log "重命名CSV文件为: $NEW_CSV_NAME"

# 运行Python脚本处理文件
log "开始运行Python脚本"
python3 "$SCRIPT_DIR/duplicate_check.py"

# 获取Python脚本生成的最新sh文件
GENERATED_SH=$(ls -t "$SCRIPT_DIR"/*.sh | grep -v "duplicate_file_process.sh" | head -n 1)
if [ -z "$GENERATED_SH" ]; then
    log "未找到生成的sh文件"
    exit 1
fi

# 添加执行权限并运行生成的sh脚本
log "执行生成的脚本: $GENERATED_SH"
chmod +x "$GENERATED_SH"
bash "$GENERATED_SH"

# 处理完成后重命名CSV文件（添加_done标记）
mv "$NEW_CSV_NAME" "${NEW_CSV_NAME%.*}_done.csv"
log "处理完成，CSV文件已标记为done"

# 清理临时文件
if [ -f "$GENERATED_SH" ]; then
    mv "$GENERATED_SH" "$TEMP_DIR/"
    log "移动生成的脚本到临时目录: $TEMP_DIR"
fi

log "所有处理已完成"