# PubMed 搜索和标注功能使用指南

MedLitAnno 现在支持直接从 PubMed 搜索医学文献并自动进行标注，基于 [PyMed 库](https://github.com/gijswobben/pymed)。

## 🚀 快速开始

### 1. 环境配置

首先配置必要的环境变量：

```bash
# PubMed API 访问配置（必须）
export PUBMED_EMAIL="your_email@example.com"  # PubMed 要求的有效邮箱
export PUBMED_TOOL="medlitanno"                # 工具标识

# LLM API 密钥（用于标注）
export DEEPSEEK_API_KEY="your_deepseek_api_key"
```

或者使用配置文件 `config/.env`：
```bash
cp config/env.example config/.env
# 编辑 .env 文件填入你的配置
```

### 2. 基本使用

#### CLI 命令行使用

```bash
# 基本搜索
medlitanno search "Helicobacter pylori rheumatoid arthritis" --max-results 20

# 疾病-细菌关系搜索
medlitanno search "autoimmune" --disease "multiple sclerosis" --bacteria "Epstein-Barr virus"

# 搜索最近文章
medlitanno search "molecular mimicry" --recent-days 30 --max-results 10

# 指定输出目录和模型
medlitanno search "gut microbiome autoimmune" \
  --max-results 50 \
  --output-dir my_results \
  --model deepseek-reasoner \
  --model-type deepseek-reasoner
```

#### Python API 使用

```python
from medlitanno.pubmed import search_and_annotate, PubMedSearcher

# 方法1: 一键搜索和标注
search_result, annotations = search_and_annotate(
    query="Helicobacter pylori molecular mimicry",
    max_results=20,
    model="deepseek-chat",
    model_type="deepseek"
)

# 方法2: 分步操作
searcher = PubMedSearcher()
result = searcher.search("gut-brain axis bacteria", max_results=50)

# 保存搜索结果
result.save_to_excel("search_results.xlsx")
```

## 🔍 搜索功能详解

### 搜索类型

1. **基本搜索**：使用 PubMed 标准查询语法
2. **疾病-细菌搜索**：专门搜索疾病与病原体关系
3. **最近文章搜索**：限定时间范围的搜索
4. **关键词搜索**：多关键词布尔查询

### 搜索参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `query` | 基本搜索查询 | "molecular mimicry autoimmune" |
| `--disease` | 疾病名称 | "rheumatoid arthritis" |
| `--bacteria` | 病原体名称 | "Helicobacter pylori" |
| `--recent-days` | 最近天数 | 30 |
| `--max-results` | 最大结果数 | 50 |
| `--output-dir` | 输出目录 | "my_results" |

### 高级搜索语法

PubMed 支持丰富的搜索语法：

```bash
# 精确短语搜索
medlitanno search '"molecular mimicry" AND "autoimmune disease"'

# 字段限定搜索
medlitanno search 'Helicobacter[Title] AND arthritis[Abstract]'

# 日期范围搜索
medlitanno search 'microbiome AND ("2020"[Date - Publication] : "2024"[Date - Publication])'

# 期刊限定搜索
medlitanno search 'gut bacteria AND "Nature"[Journal]'

# 作者搜索
medlitanno search 'microbiome AND "Smith J"[Author]'
```

## 🏷️ 标注功能

### 自动标注流程

1. **搜索文献**：从 PubMed 获取相关文章
2. **LLM 标注**：使用大模型识别实体和关系
3. **位置匹配**：自动计算标注内容的准确位置
4. **结果保存**：生成结构化的标注结果

### 标注内容

- **实体识别**：
  - 细菌/病原体 (Bacteria)
  - 疾病 (Disease)

- **关系识别**：
  - `contributes_to`：致病作用
  - `ameliorates`：保护作用  
  - `correlated_with`：统计关联
  - `biomarker_for`：诊断价值

- **证据提取**：支持关系的完整句子

### 输出格式

标注结果以多种格式保存：

1. **JSON 格式**：详细的标注数据
2. **Excel 格式**：搜索结果表格
3. **统计报告**：标注质量和数量统计
4. **汇总报告**：搜索和标注的综合分析

## 📊 使用示例

### 示例 1：研究特定疾病的微生物关联

```bash
# 搜索类风湿关节炎与微生物的关系
medlitanno search "rheumatoid arthritis microbiome" \
  --max-results 100 \
  --output-dir ra_microbiome_study \
  --model deepseek-reasoner
```

输出文件：
- `ra_microbiome_study_search.xlsx`：搜索到的文章列表
- `ra_microbiome_study_annotations.json`：详细标注结果
- `ra_microbiome_study_statistics.json`：统计信息
- `ra_microbiome_study_summary.json`：研究总结

### 示例 2：追踪最新研究进展

```python
from medlitanno.pubmed import PubMedSearcher

searcher = PubMedSearcher()

# 搜索最近30天的相关文章
recent_articles = searcher.search_recent(
    query="gut-brain axis inflammation",
    days=30,
    max_results=50
)

print(f"发现 {len(recent_articles.articles)} 篇最新文章")

# 保存结果
recent_articles.save_to_excel("latest_gut_brain_research.xlsx")
```

### 示例 3：批量处理多个查询

```python
from medlitanno.pubmed import PubMedAnnotationPipeline, PubMedSearcher
from medlitanno.annotation import MedicalAnnotationLLM

# 创建组件
searcher = PubMedSearcher()
annotator = MedicalAnnotationLLM(
    api_key="your_api_key",
    model="deepseek-chat"
)

# 创建管道
pipeline = PubMedAnnotationPipeline(searcher, annotator, "batch_results")

# 批量查询
queries = [
    "Helicobacter pylori autoimmune",
    "gut microbiome multiple sclerosis", 
    "molecular mimicry rheumatoid arthritis"
]

results = pipeline.batch_search_and_annotate(queries, max_results_per_query=20)

for query, (search_result, annotations) in results.items():
    print(f"查询 '{query}': {len(search_result.articles)} 篇文章，{len(annotations)} 个标注")
```

## ⚡ 性能和限制

### 性能特点

- **搜索速度**：通常 2-5 秒完成一次搜索
- **标注速度**：每篇文章 3-10 秒（取决于模型和网络）
- **位置匹配**：100% 成功率，平均置信度 > 0.8
- **内存使用**：轻量级，适合大批量处理

### API 限制

- **PubMed API**：遵循官方限制，内置速率控制（1秒/请求）
- **LLM API**：支持重试机制和错误恢复
- **并发限制**：不支持并发请求（PubMed 要求）

### 最佳实践

1. **合理设置结果数量**：建议单次搜索不超过 100 篇文章
2. **使用精确查询**：提高搜索结果相关性
3. **批量处理**：对于大量查询，使用批处理功能
4. **网络稳定性**：确保稳定的网络连接
5. **API 配额**：注意 LLM API 的使用限制

## 🔧 故障排除

### 常见问题

1. **"Required environment variable 'PUBMED_EMAIL' is not set"**
   - 解决：设置 `PUBMED_EMAIL` 环境变量

2. **"PyMed library is not installed"**
   - 解决：`pip install pymed`

3. **"Using SOCKS proxy" 错误**
   - 解决：网络代理问题，尝试关闭代理或安装 `httpx[socks]`

4. **搜索结果为空**
   - 检查查询语法
   - 尝试更通用的关键词
   - 确认 PubMed 中确实有相关文章

5. **标注失败**
   - 检查 API 密钥设置
   - 确认网络连接
   - 查看日志文件了解具体错误

### 调试模式

```bash
# 启用详细日志
medlitanno search "your query" --log-level DEBUG --log-file debug.log

# 查看日志
tail -f debug.log
```

## 📚 参考资料

- [PubMed 搜索语法指南](https://pubmed.ncbi.nlm.nih.gov/help/)
- [PyMed 库文档](https://github.com/gijswobben/pymed)
- [MedLitAnno 项目主页](https://github.com/chenxingqiang/medlitanno)

## 🤝 贡献和反馈

如果您在使用过程中遇到问题或有改进建议，请：

1. 查看 [GitHub Issues](https://github.com/chenxingqiang/medlitanno/issues)
2. 提交新的 Issue 或 Pull Request
3. 联系开发者：chenxingqiang@gmail.com

---

**注意**：PubMed 搜索功能基于 [PyMed 库](https://github.com/gijswobben/pymed)，该库已被原作者归档。我们在此基础上进行了集成和扩展，但请注意 PubMed API 的变化可能影响功能稳定性。
