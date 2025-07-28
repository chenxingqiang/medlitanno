# 医学文献自动标注系统
# Medical Literature Auto-Annotation System

基于LLM的医学文献自动标注系统，用于识别病原微生物与自身免疫性疾病之间的关系。

## 🎯 项目目标

原计划使用Label Studio进行人工标注，现改用LLM大模型自动化标注，提高效率并保证质量。

### 标注任务

根据`target.md`的要求，系统需要完成：

1. **实体标注**：
   - `Bacteria`（致病菌）：细菌、病毒、寄生虫、真菌等病原微生物
   - `Disease`（自身免疫性疾病）：各种自身免疫性疾病

2. **证据标注**：
   - `Evidence`（证据句）：描述实体间关系的完整句子
   - 关系类型：
     - `contributes_to`（负面影响）：病原体导致、触发、加剧疾病
     - `ameliorates`（正面影响）：病原体改善、缓解、治疗疾病
     - `correlated_with`（统计关联）：仅描述相关性，无明确因果关系
     - `biomarker_for`（应用功能）：病原体可作为疾病诊断标志物

3. **关系构建**：
   - `has_subject`：连接病原体实体
   - `has_object`：连接疾病实体

## 📊 数据概况

```
datatrain/
├── parasite-ids-390/     # 寄生虫相关疾病 (390种)
├── bacteria-ids-4937/    # 细菌相关疾病 (4937种)  
├── fugus-ids-610/        # 真菌相关疾病 (610种)
└── microorganism-ids-8228/ # 微生物相关疾病 (8228种)
```

每个Excel文件包含字段：
- `pmid`: PubMed文章ID
- `title`: 文章标题
- `abstract`: 文章摘要
- `FullJournalName`: 期刊名
- `PubDate`: 发表日期
- `doi`: DOI号

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install pandas openpyxl openai requests

# 或使用虚拟环境
python3 -m venv annotation_env
source annotation_env/bin/activate
pip install pandas openpyxl openai requests
```

### 2. 支持的模型

系统已配置以下API密钥，可直接使用：

- **DeepSeek**: `deepseek-chat` 模型
- **Qianwen**: `qwen-plus` 模型

### 3. 运行标注

#### 测试单个文件
```bash
python run_annotation.py --test
```

#### 批量处理所有文件
```bash
python run_annotation.py --batch
```

#### 比较不同模型结果
```bash
python run_annotation.py --compare
```

## 📁 系统架构

### 核心组件

1. **`auto_annotation_system.py`** - 主要标注引擎
   - `MedicalAnnotationLLM`类：核心标注功能
   - 支持多种LLM模型（DeepSeek, Qianwen）
   - 支持单文件和批量处理
   - 自动生成统计报告

2. **`run_annotation.py`** - 实用运行脚本
   - 预配置API密钥
   - 模型选择功能
   - 测试和批量处理功能
   - 模型结果比较
   - 进度显示和错误处理

3. **`convert_to_label_studio.py`** - 格式转换工具
   - 转换为Label Studio格式
   - 生成配置文件
   - 标注质量统计

4. **`demo_annotation.py`** - 演示脚本
   - 支持多模型演示
   - 文件和文本标注演示
   - 结果比较功能

### 数据流程

```
Excel文件 → LLM标注 → JSON结果 → Label Studio格式 → 人工校验
```

## 🔧 使用示例

### 单文件标注（DeepSeek）

```python
from auto_annotation_system import MedicalAnnotationLLM

# 初始化DeepSeek标注器
annotator = MedicalAnnotationLLM(
    api_key="sk-d02fca54e07f4bdfb1778aeb62ae7671",
    model="deepseek-chat",
    model_type="deepseek"
)

# 标注单个文件
results = annotator.annotate_excel_file(
    "datatrain/bacteria-ids-4937/A/Acute motor axonal neuropathy.xlsx",
    "output_deepseek.json"
)

# 生成统计
stats = annotator.generate_statistics(results)
print(stats)
```

### 单文件标注（Qianwen）

```python
# 初始化Qianwen标注器
annotator = MedicalAnnotationLLM(
    api_key="sk-296434b603504719b9f5aca8286f5166",
    model="qwen-plus",
    model_type="qianwen"
)

# 标注处理...
```

### 批量处理

```python
from auto_annotation_system import batch_process_directory

# 使用DeepSeek批量处理
batch_process_directory(
    data_dir="datatrain",
    output_dir="annotated_results_deepseek", 
    api_key="sk-d02fca54e07f4bdfb1778aeb62ae7671",
    model="deepseek-chat",
    model_type="deepseek"
)

# 使用Qianwen批量处理
batch_process_directory(
    data_dir="datatrain",
    output_dir="annotated_results_qianwen", 
    api_key="sk-296434b603504719b9f5aca8286f5166",
    model="qwen-plus",
    model_type="qianwen"
)
```

### 转换为Label Studio格式

```bash
# 转换DeepSeek结果
python convert_to_label_studio.py -i annotated_results_deepseek -o label_studio_deepseek

# 转换Qianwen结果
python convert_to_label_studio.py -i annotated_results_qianwen -o label_studio_qianwen

# 生成汇总报告
python convert_to_label_studio.py -i annotated_results_deepseek -o label_studio_deepseek --summary
```

## 📈 输出格式

### 标注结果JSON

```json
{
  "pmid": "33217007",
  "title": "文章标题",
  "abstract": "文章摘要",
  "model_info": {
    "model_type": "deepseek",
    "model_name": "deepseek-chat"
  },
  "entities": [
    {
      "text": "Campylobacter jejuni",
      "label": "Bacteria",
      "start_pos": 100,
      "end_pos": 118
    }
  ],
  "evidences": [
    {
      "text": "证据句子",
      "start_pos": 50,
      "end_pos": 150,
      "relation_type": "contributes_to"
    }
  ],
  "relations": [
    {
      "subject_text": "Campylobacter jejuni",
      "subject_label": "Bacteria", 
      "object_text": "Guillain-Barré syndrome",
      "object_label": "Disease",
      "evidence_text": "证据句子",
      "relation_type": "contributes_to"
    }
  ]
}
```

### 统计报告

```json
{
  "model_info": {
    "model_type": "deepseek",
    "model_name": "deepseek-chat"
  },
  "total_articles": 1000,
  "articles_with_entities": 800,
  "articles_with_relations": 600,
  "total_bacteria": 1200,
  "total_diseases": 900,
  "total_relations": 750,
  "relation_types": {
    "contributes_to": 400,
    "ameliorates": 100,
    "correlated_with": 200,
    "biomarker_for": 50
  }
}
```

## 🎛️ 模型配置

### 支持的模型

| 模型类型 | 模型名称 | API端点 | 特点 |
|---------|---------|---------|------|
| DeepSeek | deepseek-chat | api.deepseek.com | 推理能力强，适合复杂关系识别 |
| Qianwen | qwen-plus | dashscope.aliyuncs.com | 中文理解优秀，医学领域表现良好 |

### 模型选择建议

- **DeepSeek**: 适合需要深度推理和复杂关系分析的场景
- **Qianwen**: 适合中文医学文献，对医学术语理解较好
- **双模型**: 可以同时使用两个模型进行标注，后续比较选择最佳结果

### 自定义配置

```python
# 自定义温度参数
class CustomMedicalAnnotationLLM(MedicalAnnotationLLM):
    def _call_llm(self, messages):
        # 自定义temperature等参数
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.05,  # 更低的随机性
            max_tokens=3000,   # 更多token
            top_p=0.9
        )
        return response.choices[0].message.content.strip()
```

## 📊 质量控制

### 1. 模型比较
- 同时使用多个模型进行标注
- 比较不同模型的结果差异
- 选择表现最好的模型

### 2. 一致性检查
- 同一实体的标注一致性
- 关系类型的准确性
- 证据句的完整性

### 3. 人工校验
- 转换为Label Studio格式后进行人工校验
- 重点检查复杂关系和边界情况
- 建立标注质量反馈机制

### 4. 统计分析
- 标注覆盖率统计
- 实体和关系分布分析
- 异常情况识别

## 🔍 故障排除

### 常见问题

1. **API调用失败**
   - 检查网络连接
   - 确认API密钥有效
   - 检查账户余额

2. **JSON解析错误**
   - LLM输出格式不规范
   - 增加输出格式验证
   - 调整提示词模板

3. **模型响应慢**
   - 调整max_tokens参数
   - 优化提示词长度
   - 考虑使用更快的模型

4. **标注质量不佳**
   - 尝试不同的模型
   - 调整temperature参数
   - 优化提示词内容

### 性能优化

- 使用并行处理加速批量标注
- 缓存常见实体识别结果
- 优化提示词长度和结构
- 合理设置API调用频率

## 🚀 快速命令

```bash
# 演示功能
python demo_annotation.py --file     # 文件标注演示
python demo_annotation.py --text     # 文本标注演示
python demo_annotation.py --compare  # 比较演示结果

# 实际使用
python run_annotation.py --test      # 测试单文件
python run_annotation.py --batch     # 批量处理
python run_annotation.py --compare   # 比较模型结果

# 格式转换
python convert_to_label_studio.py -i results -o label_studio --summary
```

## 📝 开发计划

- [x] 支持DeepSeek和Qianwen模型
- [x] 模型结果比较功能
- [x] 批量处理优化
- [ ] 支持更多LLM模型（Claude, Gemini等）
- [ ] 增加主动学习功能
- [ ] 实现标注质量自动评估
- [ ] 添加实体链接和知识图谱集成
- [ ] 支持多语言标注

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 📄 许可证

Apache License 2.0

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件到项目维护者

---

**注意**：
1. 本系统已预配置DeepSeek和Qianwen的API密钥，可直接使用
2. 建议先运行测试功能验证系统工作正常
3. 大规模批量处理前请确保API账户余额充足
4. 建议结合人工校验以确保标注质量 