# Duplicate File Cleaner

用于 Synology NAS 的重复文件处理工具。自动检测和安全删除重复文件，保留指定目录下的文件或最新的文件。

## 功能特点

- 自动检测重复文件
- 安全删除机制（校验文件内容后删除）
- 详细的操作日志
- 支持定时任务

## 安装步骤

1. 克隆仓库到 NAS
2. 复制配置文件：
```bash
cp config.example.sh config.sh
```
3. 修改 config.sh 中的配置参数
4. 确保安装了必要的 Python 包：
```bash
pip3 install pandas
```

## DSM中配置定时任务

通过 DSM 控制面板设置定时任务：
1. 打开 DSM 控制面板
2. 进入"任务计划"
3. 创建新的计划任务：
   - 选择"用户定义的脚本"
   - 设置运行用户为您的用户名
   - 设置每天凌晨 5 点执行
   - 配置运行命令：
   ```bash
   # 请替换 [您的用户名]
   /var/services/homes/[您的用户名]/scripts/duplicate_file_process.sh >> /var/services/homes/[您的用户名]/scripts/duplicate_process.log 2>&1
   ```

## License
MIT

## 其他注意事项

上面的脚本执行的基础是 **存储空间分析器** 中设置了 **报告配置文件** 每次会生成重复文件的报告。

另外，你需要在自己的NAS中找到报告文件存储路径
举例：我的路径是 '/home/Log.Synology/synoreport/Delete01' 而且其中的csv文件是压缩包zip后缀

## ChangeLog
2024-11-30 新建

