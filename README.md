# Medical Literature Auto-Annotation System

🧠 **智能医学文献标注系统** - 基于大语言模型的病原微生物与自身免疫性疾病关系自动标注工具

## 📋 项目概述

本项目是一个自动化医学文献标注系统，专门用于从医学摘要中识别和标注病原微生物（细菌、病毒、寄生虫、真菌）与自身免疫性疾病之间的关系。系统支持多种大语言模型，具备强大的推理能力和网络重试机制。

### 🎯 主要功能

- **实体识别**: 自动识别病原微生物和自身免疫性疾病实体
- **关系提取**: 提取四种关系类型：`contributes_to`、`ameliorates`、`correlated_with`、`biomarker_for`
- **证据定位**: 准确定位支持关系的文本证据
- **多模型支持**: 支持 DeepSeek、DeepSeek Reasoner、Qianwen 等模型
- **断点续传**: 支持网络中断后的断点续传功能
- **批量处理**: 高效处理大规模医学文献数据

## 🚀 核心特性

### 🤖 多模型支持
- **DeepSeek Chat**: 标准对话模型，适合一般标注任务
- **DeepSeek Reasoner**: 推理增强版本，特别适合从摘要中进行复杂推理
- **Qianwen Plus**: 千问模型，提供多样化的标注视角

### 🔄 鲁棒性设计
- **网络重试机制**: 自动检测网络错误并重试
- **断点续传**: 支持任务中断后的继续处理
- **错误处理**: 详细的错误日志和失败文件记录
- **进度监控**: 实时监控处理进度和统计信息

### 📊 数据处理
- **Excel文件支持**: 直接处理PubMed导出的Excel数据
- **结构化输出**: JSON格式的标注结果，便于后续分析
- **统计报告**: 自动生成标注统计和质量报告

## 📁 项目结构

```
task-finetune-medgemma/
├── README.md                      # 项目说明文档
├── auto_annotation_system.py      # 核心标注系统
├── run_annotation.py              # 批量处理脚本
├── batch_monitor.py               # 监控和管理脚本
├── demo_annotation.py             # 演示脚本
├── monitor_progress.py            # 进度监控脚本
├── README_annotation.md           # 详细使用指南
├── target.md                      # 标注规范说明
├── arch.md                        # 系统架构文档
├── datatrain/                     # 训练数据目录
│   ├── bacteria-ids-4937/         # 细菌相关数据
│   ├── parasite-ids-390/          # 寄生虫相关数据
│   ├── fugus-ids-610/             # 真菌相关数据
│   └── microorganism-ids-8228/    # 微生物相关数据
└── src/                           # MRAgent源码（原项目）
    └── mragent/                   # MR分析工具
```

## 🛠 安装与配置

### 环境要求
- Python 3.8+
- 依赖包：`pandas`, `openpyxl`, `openai`, `requests`

### 快速安装
```bash
# 克隆项目
git clone https://github.com/chenxingqiang/medical-literature-annotation.git
cd medical-literature-annotation

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install pandas openpyxl openai requests
```

### API配置
系统已预配置API密钥，支持以下模型：
- DeepSeek API
- Qianwen API

## 🎮 使用方法

### 1. 快速开始
```bash
# 检查处理状态
python3 batch_monitor.py --status

# 启动批量处理（DeepSeek Reasoner推荐）
python3 batch_monitor.py --restart deepseek-reasoner

# 实时监控进度
python3 batch_monitor.py --monitor
```

### 2. 交互式处理
```bash
# 启动交互式批量处理
python3 run_annotation.py --batch

# 测试单个文件
python3 run_annotation.py --test

# 演示系统功能
python3 demo_annotation.py --file
```

### 3. 高级用法
```bash
# 自定义数据目录
python3 batch_monitor.py --restart deepseek-reasoner --data-dir /path/to/data

# 调整监控刷新频率
python3 batch_monitor.py --monitor --refresh 10

# 模型比较
python3 run_annotation.py --compare
```

## 📊 输出格式

### 标注结果 (JSON)
```json
{
  "pmid": "12345678",
  "title": "文章标题",
  "abstract": "文章摘要",
  "entities": [
    {
      "text": "Helicobacter pylori",
      "label": "Bacteria",
      "start_pos": 45,
      "end_pos": 63
    }
  ],
  "evidences": [
    {
      "text": "H. pylori infection contributes to gastric autoimmunity",
      "start_pos": 120,
      "end_pos": 175,
      "relation_type": "contributes_to"
    }
  ],
  "relations": [
    {
      "subject_text": "Helicobacter pylori",
      "object_text": "gastric autoimmunity",
      "evidence_text": "H. pylori infection contributes to gastric autoimmunity",
      "relation_type": "contributes_to"
    }
  ],
  "model_info": {
    "model_type": "deepseek-reasoner",
    "model_name": "deepseek-reasoner"
  }
}
```

### 统计报告
```json
{
  "model_info": {
    "model_type": "deepseek-reasoner",
    "model_name": "deepseek-reasoner"
  },
  "total_articles": 150,
  "articles_with_entities": 145,
  "articles_with_relations": 120,
  "total_bacteria": 89,
  "total_diseases": 234,
  "total_relations": 156,
  "relation_types": {
    "contributes_to": 89,
    "ameliorates": 23,
    "correlated_with": 34,
    "biomarker_for": 10
  }
}
```

## 🔧 关系类型说明

| 关系类型 | 描述 | 示例 |
|---------|------|------|
| `contributes_to` | 病原体导致、触发、加剧疾病 | "H. pylori contributes to gastric autoimmunity" |
| `ameliorates` | 病原体改善、缓解疾病 | "Probiotics ameliorate inflammatory bowel disease" |
| `correlated_with` | 统计学相关但机制不明 | "EBV infection is correlated with MS risk" |
| `biomarker_for` | 可作为疾病诊断标志物 | "Anti-CCP antibodies are biomarkers for RA" |

## 📈 性能特点

- **处理速度**: 每个文件约1-2分钟（取决于文章数量和模型）
- **准确率**: DeepSeek Reasoner模型在复杂推理任务上表现优异
- **可扩展性**: 支持大规模数据集的批量处理
- **容错性**: 完善的错误处理和重试机制

## 🛡️ 稳定性保障

### 网络稳定性
- 自动检测网络错误
- 智能重试机制（最多5次）
- 失败文件单独记录和处理

### 断点续传
- 自动跳过已处理文件
- 支持任务中断后继续
- 完整的处理状态追踪

### 监控和调试
- 实时进度监控
- 详细的处理日志
- 统计信息和质量报告

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发环境设置
```bash
git clone https://github.com/chenxingqiang/medical-literature-annotation.git
cd medical-literature-annotation
python3 -m venv dev_env
source dev_env/bin/activate
pip install -r requirements.txt
```

### 代码规范
- 遵循PEP 8代码风格
- 添加必要的注释和文档
- 提交前进行充分测试

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- 项目维护者: chenxingqiang
- 邮箱: [您的邮箱]
- GitHub: [@chenxingqiang](https://github.com/chenxingqiang)

## 🙏 致谢

- 感谢 DeepSeek 和 Qianwen 提供的优秀语言模型
- 感谢开源社区的支持和贡献
- 特别感谢医学领域专家的指导和建议

---

**⭐ 如果这个项目对您有帮助，请给我们一个Star！** 