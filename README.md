# MedLitAnno: Medical Literature Annotation System

[![GitHub](https://img.shields.io/github/license/chenxingqiang/medlitanno)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![PyPI](https://img.shields.io/badge/pypi-v1.0.0-blue)](https://pypi.org/project/medlitanno/)
[![CI](https://img.shields.io/badge/CI-passing-brightgreen)](https://github.com/chenxingqiang/medlitanno/actions)

MedLitAnno is a powerful tool for automated annotation of medical literature, designed to extract structured information about bacteria-disease relationships from scientific texts. It also includes MRAgent, an innovative automated agent for causal knowledge discovery in disease research via Mendelian Randomization (MR).

## 🌟 Features

### Medical Literature Annotation
- **Multi-model Support**: Use OpenAI, DeepSeek, DeepSeek Reasoner, or Qianwen models
- **Robust Processing**: Breakpoint resume and error retry mechanisms
- **Comprehensive Annotation**: Entity recognition, relation extraction, evidence detection
- **Batch Processing**: Process entire directories of Excel files
- **Progress Monitoring**: Track annotation progress and manage batch processing
- **Format Conversion**: Export to Label Studio compatible format

### MRAgent: Causal Knowledge Discovery
- **Automated Literature Analysis**: Scans scientific literature to discover potential exposure-outcome pairs
- **Causal Inference**: Performs Mendelian Randomization using GWAS data
- **Knowledge Discovery Mode**: Autonomously identifies potential causal factors for diseases
- **Causal Validation Mode**: Validates specific causal hypotheses
- **GWAS Integration**: Seamless integration with OpenGWAS database

## 🚀 Installation

### From PyPI (Recommended)

```bash
pip install medlitanno
```

### From Source

```bash
# Clone the repository
git clone https://github.com/chenxingqiang/medlitanno.git
cd medlitanno

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

## ⚙️ API Key Configuration

Set your API keys as environment variables:

```bash
# For DeepSeek models
export DEEPSEEK_API_KEY="your-deepseek-api-key"

# For Qianwen models
export QIANWEN_API_KEY="your-qianwen-api-key"

# For OpenAI models (optional)
export OPENAI_API_KEY="your-openai-api-key"

# For MR analysis (optional)
export OPENGWAS_JWT="your-opengwas-jwt-token"
```

## 📊 Usage

### Medical Literature Annotation

#### Command Line Interface

```bash
# Annotate medical literature
medlitanno annotate --data-dir datatrain --model deepseek-chat
```

#### Python API

```python
from medlitanno.annotation import MedicalAnnotationLLM
import os

# Initialize the annotator
annotator = MedicalAnnotationLLM(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    model="deepseek-chat",
    model_type="deepseek"
)

# Annotate text
text = "Helicobacter pylori infection is associated with gastric cancer."
result = annotator.annotate_text(text)

# Print results
print(f"Entities: {result.entities}")
print(f"Relations: {result.relations}")
print(f"Evidences: {result.evidences}")
```

### MRAgent: Causal Knowledge Discovery

#### Command Line Interface

```bash
# Knowledge Discovery mode
medlitanno mr --outcome "back pain" --model gpt-4o

# Causal Validation mode
medlitanno mr --exposure "osteoarthritis" --outcome "back pain" --mode causal
```

#### Python API

```python
from medlitanno.mragent import MRAgent, MRAgentOE
import os

# Knowledge Discovery mode
agent = MRAgent(
    outcome="back pain",
    AI_key=os.environ.get("OPENAI_API_KEY"),
    LLM_model="gpt-4o",
    gwas_token=os.environ.get("OPENGWAS_JWT")
)
agent.run()

# Causal Validation mode
agent_oe = MRAgentOE(
    exposure="osteoarthritis",
    outcome="back pain",
    AI_key=os.environ.get("OPENAI_API_KEY"),
    LLM_model="gpt-4o",
    gwas_token=os.environ.get("OPENGWAS_JWT")
)
agent_oe.run()
```

## 📄 Output Format

### Annotation System

The annotation system extracts:

1. **Entities**: Bacteria and Disease mentions
2. **Relations**: Connections between entities with relation types
3. **Evidences**: Text spans supporting the relations

#### Relation Types

- `contributes_to`: Bacteria contributes to disease development
- `ameliorates`: Bacteria improves or alleviates disease
- `correlated_with`: Bacteria and disease show correlation
- `biomarker_for`: Bacteria serves as a biomarker for disease

### MRAgent System

MRAgent provides:

1. **Literature Analysis**: Summary of relevant scientific papers
2. **Potential Exposures**: List of potential causal factors
3. **MR Results**: Statistical evidence for causal relationships
4. **Visualizations**: Forest plots and other visual representations
5. **Recommendations**: Insights for further research

## 🚀 Performance

- **Annotation Speed**: ~30-60 seconds per document (depends on model and text length)
- **MR Analysis**: Processes hundreds of articles and GWAS datasets efficiently
- **Accuracy**: Comparable to manual annotation and analysis in controlled tests

## 💪 Stability

- **Breakpoint Resume**: Automatically continues from the last processed file
- **Error Retry**: Automatically retries failed operations
- **Progress Monitoring**: Track progress in real-time

## 📋 Project Structure

```
medlitanno/
├── src/                # Source code
│   └── medlitanno/     # Main package
│       ├── annotation/ # Annotation system
│       ├── common/     # Shared utilities
│       └── mragent/    # MR analysis (optional)
├── docs/               # Documentation
│   ├── images/         # Documentation images
│   └── ...
├── examples/           # Example scripts
├── tests/              # Unit tests
├── scripts/            # Utility scripts
├── config/             # Configuration files
└── ...
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

For questions or feedback, please contact [chenxingqiang@gmail.com](mailto:chenxingqiang@gmail.com).

---

**Note**: This package incorporates technology from [MRAgent](https://github.com/xuwei1997/MRAgent), an innovative automated agent for causal knowledge discovery in disease research via Mendelian Randomization. 