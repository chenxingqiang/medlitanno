# MedLitAnno: Medical Literature Annotation System

[![GitHub](https://img.shields.io/github/license/chenxingqiang/medlitanno)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![PyPI](https://img.shields.io/badge/pypi-v1.1.0-blue)](https://pypi.org/project/medlitanno/)
[![CI](https://img.shields.io/badge/CI-passing-brightgreen)](https://github.com/chenxingqiang/medlitanno/actions)

MedLitAnno is a comprehensive medical literature analysis platform that combines automated annotation, PubMed search integration, and causal knowledge discovery. Extract structured information about bacteria-disease relationships from scientific texts, search and annotate PubMed literature automatically, and discover causal relationships through Mendelian Randomization (MR) analysis.

## 🌟 Features

### 🔍 PubMed Literature Search & Annotation
- **Direct PubMed Integration**: Search medical literature using keywords, diseases, bacteria, or recent publications
- **Automated Annotation Pipeline**: Seamlessly combine literature search with LLM-powered annotation
- **Multiple Search Strategies**: Basic search, disease-bacteria relationships, recent articles, keyword combinations
- **Excel Export**: Save search results with comprehensive metadata and citation information
- **Rate-Limited API Access**: Compliant with PubMed guidelines for responsible usage

### 📝 Advanced Medical Literature Annotation
- **Multi-model Support**: Use OpenAI, DeepSeek, DeepSeek Reasoner, or Qianwen models
- **Automatic Position Matching**: Intelligent text position calculation with 100% success rate
- **Smart Content Recognition**: LLM focuses on content identification while system handles positioning
- **Robust Processing**: Breakpoint resume and error retry mechanisms for network stability
- **Comprehensive Annotation**: Entity recognition, relation extraction, evidence detection
- **Batch Processing**: Process entire directories of Excel files with progress monitoring
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

## ⚙️ Configuration

### API Keys and Environment Setup

Set your API keys and configuration as environment variables:

```bash
# For LLM models
export DEEPSEEK_API_KEY="your-deepseek-api-key"
export QIANWEN_API_KEY="your-qianwen-api-key"
export OPENAI_API_KEY="your-openai-api-key"  # Optional

# For PubMed search (required for literature search)
export PUBMED_EMAIL="your_email@example.com"  # Required by PubMed API
export PUBMED_TOOL="medlitanno"              # Tool identifier

# For MR analysis (optional)
export OPENGWAS_JWT="your-opengwas-jwt-token"
```

### Configuration File

You can also create a `.env` file in your project directory:

```bash
# Copy the example configuration
cp config/env.example .env
# Edit .env with your actual API keys and settings
```

## 📊 Usage

### 🔍 PubMed Literature Search

#### Command Line Interface

```bash
# Search PubMed and automatically annotate results
medlitanno search "Helicobacter pylori gastric cancer" --max-results 50

# Search for disease-bacteria relationships
medlitanno search "diabetes microbiome" --disease "diabetes" --bacteria "gut bacteria"

# Search recent publications (last 30 days)
medlitanno search "COVID-19 microbiome" --recent-days 30

# Search and save results to Excel (without annotation)
medlitanno search "inflammatory bowel disease" --output-dir ./results --max-results 100
```

#### Python API

```python
from medlitanno.pubmed import PubMedSearcher, search_and_annotate
import os

# Initialize PubMed searcher
searcher = PubMedSearcher(
    email=os.environ.get("PUBMED_EMAIL"),
    tool="medlitanno"
)

# Search for articles
results = searcher.search("Helicobacter pylori gastric cancer", max_results=50)
print(f"Found {len(results.articles)} articles")

# Search and automatically annotate
search_and_annotate(
    query="microbiome inflammatory disease",
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    model="deepseek-chat",
    max_results=20,
    output_dir="./results"
)
```

### 📝 Medical Literature Annotation

#### Command Line Interface

```bash
# Annotate medical literature
medlitanno annotate --data-dir datatrain --model deepseek-chat

# Use DeepSeek Reasoner for enhanced inference
medlitanno annotate --data-dir datatrain --model deepseek-reasoner --model-type deepseek
```

#### Python API

```python
from medlitanno.annotation import MedicalAnnotationLLM
import os

# Initialize the annotator with automatic position matching
annotator = MedicalAnnotationLLM(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    model="deepseek-chat",
    model_type="deepseek"
)

# Annotate text with automatic position calculation
text = "Helicobacter pylori infection is associated with gastric cancer."
result = annotator.annotate_text(text)

# Print results with position information
print(f"Entities: {result.entities}")
for entity in result.entities:
    print(f"  - {entity.text} ({entity.label}): pos {entity.start_pos}-{entity.end_pos}, confidence: {entity.confidence:.2f}")

print(f"Relations: {result.relations}")
print(f"Evidences: {result.evidences}")
for evidence in result.evidences:
    print(f"  - {evidence.text}: pos {evidence.start_pos}-{evidence.end_pos}, confidence: {evidence.confidence:.2f}")
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

### PubMed Search Results

PubMed search provides:

1. **Article Metadata**: Title, abstract, authors, publication date, journal
2. **Citation Information**: PMID, DOI, publication details
3. **Search Statistics**: Total results, query details, search timestamp
4. **Excel Export**: Structured data export for further analysis

### Annotation System

The annotation system extracts structured information with automatic position matching:

1. **Entities**: Bacteria and Disease mentions with precise text positions
2. **Relations**: Connections between entities with relation types
3. **Evidences**: Text spans supporting the relations with confidence scores
4. **Position Statistics**: Success rates and confidence metrics for quality assessment

#### Relation Types

- `contributes_to`: Bacteria contributes to disease development
- `ameliorates`: Bacteria improves or alleviates disease
- `correlated_with`: Bacteria and disease show correlation
- `biomarker_for`: Bacteria serves as a biomarker for disease

#### Position Matching Features

- **100% Success Rate**: Intelligent matching strategies ensure reliable position detection
- **Multiple Strategies**: Exact, case-insensitive, normalized, fuzzy, and partial matching
- **Confidence Scoring**: Average confidence >0.8 for quality assessment
- **Automatic Fallback**: Progressive matching strategies for robust results

### MRAgent System

MRAgent provides:

1. **Literature Analysis**: Summary of relevant scientific papers
2. **Potential Exposures**: List of potential causal factors
3. **MR Results**: Statistical evidence for causal relationships
4. **Visualizations**: Forest plots and other visual representations
5. **Recommendations**: Insights for further research

## 🚀 Performance

### Literature Search
- **PubMed Integration**: Real-time search with rate limiting (3 requests/second)
- **Search Speed**: ~2-5 seconds per query (depends on result count)
- **Result Processing**: Handles thousands of articles efficiently

### Annotation System
- **Processing Speed**: ~30-60 seconds per document (depends on model and text length)
- **Position Matching**: 100% success rate with <1 second processing per document
- **Batch Processing**: Optimized for large-scale literature analysis
- **Accuracy**: Comparable to manual annotation in controlled tests

### MR Analysis
- **Literature Processing**: Handles hundreds of articles and GWAS datasets efficiently
- **Causal Discovery**: Automated analysis of complex exposure-outcome relationships

## 💪 Stability & Reliability

### Network Resilience
- **Automatic Retry**: Smart retry mechanisms for network instability
- **Rate Limiting**: Compliant with API guidelines and rate limits
- **Connection Recovery**: Robust handling of network interruptions

### Processing Reliability
- **Breakpoint Resume**: Automatically continues from the last processed file
- **Error Recovery**: Graceful handling of parsing and processing errors
- **Progress Monitoring**: Real-time tracking with detailed statistics
- **Data Validation**: Comprehensive validation of results and outputs

## 📋 Project Structure

```
medlitanno/
├── src/                    # Source code
│   └── medlitanno/         # Main package
│       ├── annotation/     # Annotation system with position matching
│       ├── pubmed/         # PubMed search integration
│       ├── common/         # Shared utilities and base classes
│       └── mragent/        # MR analysis (optional, requires biopython)
├── docs/                   # Documentation
│   ├── PUBMED_SEARCH_GUIDE.md  # PubMed search usage guide
│   ├── README_annotation.md    # Annotation system documentation
│   └── ...
├── examples/               # Example scripts and demos
│   ├── pubmed_search_demo.py   # PubMed search examples
│   ├── position_matching_demo.py # Position matching examples
│   └── ...
├── tests/                  # Unit tests
├── scripts/                # Utility scripts
├── config/                 # Configuration files
│   ├── env.example         # Environment configuration template
│   └── requirements.txt    # Dependencies
├── CHANGELOG.md            # Version history
└── ...
```

## 📚 Documentation

- **[PubMed Search Guide](docs/PUBMED_SEARCH_GUIDE.md)**: Complete guide for literature search functionality
- **[Annotation Documentation](docs/README_annotation.md)**: Detailed annotation system documentation
- **[Setup Guide](docs/SETUP.md)**: Installation and configuration instructions
- **[Examples](examples/)**: Working examples and demo scripts

## 🔄 Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and feature updates.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/chenxingqiang/medlitanno.git
cd medlitanno

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

For questions or feedback, please contact [joy66777@gmail.com](mailto:joy66777@gmail.com).

## 🙏 Acknowledgments

- **[MRAgent](https://github.com/xuwei1997/MRAgent)**: Innovative automated agent for causal knowledge discovery via Mendelian Randomization
- **[PyMed](https://github.com/gijswobben/pymed)**: Python library for PubMed API access
- **[OpenGWAS](https://gwas.mrcieu.ac.uk/)**: GWAS summary data for causal inference

---

**Latest Version**: v1.1.0 - Now with PubMed search integration and automatic position matching! 