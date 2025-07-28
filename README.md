# MedLitAnno: Medical Literature Annotation System

[![GitHub](https://img.shields.io/github/license/chenxingqiang/medlitanno)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![CI](https://img.shields.io/badge/CI-passing-brightgreen)](https://github.com/chenxingqiang/medlitanno/actions)

MedLitAnno is a powerful tool for automated annotation of medical literature, designed to extract structured information about bacteria-disease relationships from scientific texts.

## 🌟 Features

- **Multi-model Support**: Use OpenAI, DeepSeek, DeepSeek Reasoner, or Qianwen models
- **Robust Processing**: Breakpoint resume and error retry mechanisms
- **Comprehensive Annotation**: Entity recognition, relation extraction, evidence detection
- **Batch Processing**: Process entire directories of Excel files
- **Progress Monitoring**: Track annotation progress and manage batch processing
- **Format Conversion**: Export to Label Studio compatible format
- **MR Analysis**: Optional Mendelian Randomization analysis (requires additional dependencies)

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

## 🚀 Installation

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

### Command Line Interface

```bash
# Annotate medical literature
medlitanno annotate --data-dir datatrain --model deepseek-chat

# Run MR analysis (Knowledge Discovery mode)
medlitanno mr --outcome "back pain" --model gpt-4o

# Test the installation
medlitanno test
```

### Python API

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

## 📄 Output Format

The annotation system extracts:

1. **Entities**: Bacteria and Disease mentions
2. **Relations**: Connections between entities with relation types
3. **Evidences**: Text spans supporting the relations

### Relation Types

- `contributes_to`: Bacteria contributes to disease development
- `ameliorates`: Bacteria improves or alleviates disease
- `correlated_with`: Bacteria and disease show correlation
- `biomarker_for`: Bacteria serves as a biomarker for disease

## 🚀 Performance

- **Speed**: ~30-60 seconds per document (depends on model and text length)
- **Accuracy**: Comparable to manual annotation in controlled tests

## 💪 Stability

- **Breakpoint Resume**: Automatically continues from the last processed file
- **Error Retry**: Automatically retries failed annotations
- **Progress Monitoring**: Track annotation progress in real-time

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

For questions or feedback, please contact [chenxingqiang@gmail.com](mailto:chenxingqiang@gmail.com).

---

**Note**: This repository has been cleaned up and reorganized into a proper Python package structure. Old test files and demos have been removed. 