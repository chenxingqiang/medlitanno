# 🧠 医学文献自动标注系统

[![GitHub](https://img.shields.io/github/license/chenxingqiang/medical-literature-annotation)](https://github.com/chenxingqiang/medical-literature-annotation/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/chenxingqiang/medical-literature-annotation/workflows/CI/badge.svg)](https://github.com/chenxingqiang/medical-literature-annotation/actions)

> 基于大语言模型的病原微生物与自身免疫性疾病关系自动标注工具  
> LLM-based Automated Annotation Tool for Pathogen-Autoimmune Disease Relationships

## 🎯 项目概述

本项目是一个智能化的医学文献标注系统，专门用于自动识别和标注病原微生物与自身免疫性疾病之间的关系。系统支持多种大语言模型，具有断点续传、错误重试等稳定性保障功能。

### ✨ 核心功能

- 🤖 **多模型支持**: DeepSeek Chat/Reasoner, Qianwen Plus
- 🔍 **实体识别**: 自动识别病原微生物(Bacteria)和疾病(Disease)
- 🔗 **关系抽取**: 识别4种关系类型 (`contributes_to`, `ameliorates`, `correlated_with`, `biomarker_for`)
- 📝 **证据提取**: 提取支持关系的文本证据
- 🛡️ **稳定保障**: 断点续传、自动重试、进度监控
- 🔒 **安全配置**: 环境变量管理API密钥

## 🚀 快速开始

### 1. 安装系统

```bash
# 克隆项目
git clone https://github.com/chenxingqiang/medical-literature-annotation.git
cd medical-literature-annotation

# 运行安装脚本
./scripts/setup.sh
```

### 2. 配置API密钥

```bash
# 方法1: 设置环境变量
export DEEPSEEK_API_KEY=your_deepseek_api_key
export QIANWEN_API_KEY=your_qianwen_api_key

# 方法2: 使用配置文件
cp config/env.example .env
# 编辑 .env 文件填入您的API密钥
```

### 3. 运行系统

```bash
# 使用便捷脚本
./scripts/run.sh

# 或直接运行
python3 src/annotation/run_annotation.py
```

### 4. 监控进度

```bash
# 实时监控
./scripts/monitor.sh monitor

# 查看状态
./scripts/monitor.sh status

# 重启处理
./scripts/monitor.sh restart deepseek-reasoner
```

## 📁 项目结构

```
medical-literature-annotation/
├── 📂 src/                    # 源代码
│   ├── annotation/            # 标注系统核心
│   │   ├── auto_annotation_system.py
│   │   ├── batch_monitor.py
│   │   ├── run_annotation.py
│   │   └── convert_to_label_studio.py
│   └── mragent/              # MRAgent相关模块
├── 📂 docs/                   # 文档
│   ├── SETUP.md              # 安装指南
│   ├── README_annotation.md  # 标注系统文档
│   ├── 使用指南.md            # 中文使用指南
│   ├── arch.md               # 架构文档
│   └── target.md             # 标注规范
├── 📂 scripts/               # 便捷脚本
│   ├── setup.sh              # 安装脚本
│   ├── run.sh                # 运行脚本
│   └── monitor.sh            # 监控脚本
├── 📂 examples/              # 示例代码
│   └── quick_start.py        # 快速开始示例
├── 📂 tests/                 # 测试文件
│   └── test_annotation.py    # 基础测试
├── 📂 config/                # 配置文件
│   ├── requirements.txt      # Python依赖
│   └── env.example           # 环境变量示例
├── 📂 output/                # 输出结果
├── 📂 logs/                  # 日志文件
├── 📂 .github/               # GitHub配置
│   ├── workflows/ci.yml      # CI/CD流程
│   └── ISSUE_TEMPLATE/       # Issue模板
└── README.md                 # 主文档
```

## 🔧 使用方法

### 基础使用

```python
from src.annotation.auto_annotation_system import MedicalAnnotationLLM

# 创建标注器
annotator = MedicalAnnotationLLM(
    api_key="your_api_key",
    model="deepseek-reasoner",
    model_type="deepseek-reasoner"
)

# 标注文本
result = annotator.annotate_text(
    title="Your paper title",
    abstract="Your paper abstract",
    pmid="paper_id"
)

# 查看结果
print(f"实体: {len(result.entities)}")
print(f"关系: {len(result.relations)}")
print(f"证据: {len(result.evidence)}")
```

### 批量处理

```python
from src.annotation.auto_annotation_system import batch_process_directory

# 批量处理Excel文件
batch_process_directory(
    data_dir="datatrain",
    model="deepseek-reasoner",
    model_type="deepseek-reasoner"
)
```

## 📊 支持的模型

| 模型 | 特点 | 适用场景 |
|------|------|----------|
| DeepSeek Chat | 速度快，成本低 | 大批量处理 |
| DeepSeek Reasoner | 推理能力强 | 复杂关系识别 |
| Qianwen Plus | 中文理解优秀 | 中文医学文献 |

## 🔗 关系类型

- **contributes_to**: 病原体导致或加重疾病
- **ameliorates**: 病原体改善或缓解疾病  
- **correlated_with**: 病原体与疾病存在统计关联
- **biomarker_for**: 病原体可作为疾病的生物标志物

## 📈 性能特点

- ⚡ **高效处理**: 支持批量处理数千个文件
- 🛡️ **稳定可靠**: 断点续传，网络异常自动重试
- 📊 **实时监控**: 进度跟踪，状态查看
- 🔄 **灵活配置**: 多种模型选择，参数可调

## 🧪 运行测试

```bash
# 运行基础测试
python3 tests/test_annotation.py

# 运行快速示例
python3 examples/quick_start.py
```

## 📚 文档

- [📖 安装指南](docs/SETUP.md) - 详细安装和配置说明
- [📖 使用指南](docs/使用指南.md) - 完整使用教程
- [📖 标注规范](docs/target.md) - 标注任务说明
- [📖 架构文档](docs/arch.md) - 系统架构介绍

## 🤝 贡献

欢迎提交Issue和Pull Request！

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系我们

- **项目主页**: https://github.com/chenxingqiang/medical-literature-annotation
- **问题反馈**: [GitHub Issues](https://github.com/chenxingqiang/medical-literature-annotation/issues)
- **邮箱**: chenxingqiang@example.com

---

**⭐ 如果这个项目对您有帮助，请给我们一个星标！** 