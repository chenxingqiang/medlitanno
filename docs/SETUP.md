# 🚀 快速开始指南

## 1. 环境配置

### 设置环境变量
```bash
# 方法1: 直接设置环境变量
export DEEPSEEK_API_KEY=your_deepseek_api_key_here
export QIANWEN_API_KEY=your_qianwen_api_key_here

# 方法2: 使用配置文件
cp env.example .env
# 编辑 .env 文件，填入您的API密钥
```

### 验证配置
```bash
# 检查环境变量是否设置成功
echo $DEEPSEEK_API_KEY
echo $QIANWEN_API_KEY
```

## 2. 安装依赖

```bash
# 创建虚拟环境 (推荐)
python3 -m venv annotation_env
source annotation_env/bin/activate  # Linux/Mac
# 或
annotation_env\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

## 3. 准备数据

将您的Excel数据文件放置在 `datatrain/` 目录下，按以下结构组织：
```
datatrain/
├── category1/
│   ├── A/
│   │   ├── Disease1.xlsx
│   │   └── Disease2.xlsx
│   └── B/
│       └── Disease3.xlsx
└── category2/
    └── ...
```

## 4. 运行标注

### 批量处理所有文件
```bash
# 使用DeepSeek模型
python3 -c "
from auto_annotation_system import batch_process_directory
batch_process_directory(
    data_dir='datatrain',
    model='deepseek-chat',
    model_type='deepseek'
)
"

# 使用DeepSeek Reasoner模型 (更强推理能力)
python3 -c "
from auto_annotation_system import batch_process_directory
batch_process_directory(
    data_dir='datatrain',
    model='deepseek-reasoner',
    model_type='deepseek-reasoner'
)
"

# 使用Qianwen模型
python3 -c "
from auto_annotation_system import batch_process_directory
batch_process_directory(
    data_dir='datatrain',
    model='qwen-plus',
    model_type='qianwen'
)
"
```

### 使用便捷脚本
```bash
# 交互式运行
python3 run_annotation.py

# 监控进度
python3 batch_monitor.py --monitor

# 查看状态
python3 batch_monitor.py --status

# 重启处理
python3 batch_monitor.py --restart deepseek-reasoner
```

## 5. 查看结果

标注结果保存在各疾病目录的 `annotation/` 子目录下：
```
datatrain/category1/A/Disease1/annotation/
├── Disease1_annotated_deepseek.json
├── Disease1_annotated_deepseek-reasoner.json
└── Disease1_annotated_qianwen.json
```

## 6. 故障排除

### 常见问题

**Q: 提示API密钥未设置**
```bash
# 确保环境变量正确设置
export DEEPSEEK_API_KEY=sk-your-key-here
export QIANWEN_API_KEY=sk-your-key-here
```

**Q: 网络连接不稳定**
- 系统支持自动重试和断点续传
- 可以随时中断并重新运行，已处理的文件会被跳过

**Q: 模块导入错误**
```bash
# 确保在虚拟环境中运行
source annotation_env/bin/activate
pip install -r requirements.txt
```

**Q: 数据文件格式问题**
- 确保Excel文件包含 'Title', 'Abstract', 'PMID' 列
- 检查文件路径和权限

### 获取帮助

- 查看 [README.md](README.md) 了解详细功能
- 提交 [GitHub Issues](https://github.com/chenxingqiang/medical-literature-annotation/issues) 报告问题
- 参考 [target.md](target.md) 了解标注规范

## 7. 高级配置

### 自定义参数
```python
from auto_annotation_system import batch_process_directory

batch_process_directory(
    data_dir='datatrain',
    model='deepseek-reasoner',
    model_type='deepseek-reasoner',
    max_retries=5,      # 最大重试次数
    retry_delay=10      # 重试延迟(秒)
)
```

### 性能优化建议
- DeepSeek Reasoner: 推理能力最强，适合复杂关系抽取
- DeepSeek Chat: 速度较快，适合大批量处理
- Qianwen Plus: 平衡性能，适合中等规模数据

---

🎉 **准备就绪！** 现在您可以开始使用智能医学文献标注系统了。 