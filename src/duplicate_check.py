#!/usr/bin/env python3
import pandas as pd
import os
import sys
from datetime import datetime
import configparser
import subprocess

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(os.path.dirname(script_dir), 'config.sh')
    
    # 解析 shell 配置文件
    config = {}
    try:
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip().strip('"')
    except Exception as e:
        print(f"配置文件读取错误: {str(e)}")
        sys.exit(1)
    
    return config

def create_deletion_script(csv_file, output_script, config):
    try:
        df = pd.read_csv(csv_file, 
                        delimiter=config.get('CSV_DELIMITER', '\t'),
                        encoding=config.get('CSV_ENCODING', 'utf-16le'))
    except Exception as e:
        print(f"读取文件时出错: {str(e)}")
        return
    
    preserve_path = config.get('PRESERVE_PATH', '/volume3/homes/')
    
    with open(output_script, 'w', encoding='utf-8') as f:
        f.write('#!/bin/bash\n\n')
        f.write('# 删除重复文件的脚本\n')
        f.write('# 此脚本会验证文件内容确保安全删除\n\n')
        
        # 添加日志函数
        f.write('log_file="duplicate_deletion_log_$(date +%Y%m%d_%H%M%S).txt"\n\n')
        f.write('log() {\n')
        f.write('    echo "$(date "+%Y-%m-%d %H:%M:%S") $1" | tee -a "$log_file"\n')
        f.write('}\n\n')
        
        # 添加验证函数
        f.write('verify_identical() {\n')
        f.write('    file1="$1"\n')
        f.write('    file2="$2"\n')
        f.write('    if [ ! -f "$file1" ] || [ ! -f "$file2" ]; then\n')
        f.write('        return 1\n')
        f.write('    fi\n')
        f.write('    cmp -s "$file1" "$file2"\n')
        f.write('    return $?\n')
        f.write('}\n\n')
        
        f.write('log "开始处理重复文件..."\n\n')
        
        deleted_size = 0
        groups = df.groupby('Group')
        
        for group_num, group_data in groups:
            if len(group_data) == 1:
                continue
                
            files = group_data[['File', 'Size(Byte)', 'Modified Time']].values.tolist()
            
            sizes = set(file[1] for file in files)
            if len(sizes) != 1:
                f.write(f'log "Group {group_num} 中文件大小不一致，跳过"\n')
                continue
            
            keep_file = None
            for file_info in files:
                file_path = file_info[0]
                if preserve_path in file_path:
                    keep_file = file_path
                    break
            
            if not keep_file:
                newest_file = sorted(files, key=lambda x: x[2])[-1]
                keep_file = newest_file[0]
            
            f.write(f'log "处理 Group {group_num}:"\n')
            f.write(f'log "保留文件: {keep_file}"\n')
            
            for file_info in files:
                file_path = file_info[0]
                file_size = file_info[1]
                if file_path != keep_file:
                    f.write(f'if verify_identical "{keep_file}" "{file_path}"; then\n')
                    f.write(f'    rm "{file_path}"\n')
                    f.write(f'    log "已删除: {file_path}"\n')
                    f.write('else\n')
                    f.write(f'    log "警告: {file_path} 内容不同，跳过删除"\n')
                    f.write('fi\n\n')
                    deleted_size += file_size
        
        f.write(f'log "预计释放空间: {deleted_size / (1024**3):.2f} GB"\n')
        f.write('log "删除操作完成"\n')

if __name__ == "__main__":
    config = load_config()
    script_dir = config.get('SCRIPT_DIR', os.path.dirname(os.path.abspath(__file__)))
    
    csv_files = [f for f in os.listdir(script_dir) if f.endswith('.csv')]
    
    if csv_files:
        print("当前目录下的CSV文件：")
        for i, file in enumerate(csv_files, 1):
            print(f"{i}. {file}")
        try:
            choice = input("\n请输入要处理的CSV文件编号（或直接输入文件名）: ")
            if choice.isdigit() and 1 <= int(choice) <= len(csv_files):
                csv_file = os.path.join(script_dir, csv_files[int(choice)-1])
            else:
                csv_file = os.path.join(script_dir, choice)
        except (ValueError, IndexError):
            print("输入无效")
            sys.exit(1)
    else:
        csv_file = input("请输入CSV文件名: ")
        csv_file = os.path.join(script_dir, csv_file)

    if not os.path.exists(csv_file):
        print(f"错误：找不到文件 {csv_file}")
        sys.exit(1)

    base_name = os.path.splitext(os.path.basename(csv_file))[0]
    
    if not any(part.count('-') == 2 and len(part) == 10 for part in base_name.split('_')):
        current_date = datetime.now().strftime('%Y-%m-%d')
        output_script = os.path.join(script_dir, f"{base_name}_{current_date}.sh")
    else:
        output_script = os.path.join(script_dir, f"{base_name}.sh")
        
    create_deletion_script(csv_file, output_script, config)
    print(f"删除脚本已生成: {output_script}")
    print("请检查脚本内容后再执行")