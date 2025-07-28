# MRAgent Project Architecture Summary

## Project Overview

**MRAgent** is an innovative LLM-based automated agent designed for causal knowledge discovery in disease research through Mendelian Randomization (MR) analysis. The project leverages Large Language Models to autonomously scan scientific literature, identify potential exposure-outcome pairs, and perform comprehensive MR causal inference using extensive Genome-Wide Association Study (GWAS) data.

## Core Purpose

The primary goal of MRAgent is to address the challenge in medical research where MR analysis typically requires pre-identification of exposure-outcome pairs from clinical experience or literature. MRAgent automates this process by:

1. **Literature Mining**: Autonomously scanning PubMed for relevant scientific papers
2. **Relationship Discovery**: Identifying potential causal relationships between diseases and exposures/outcomes
3. **Automated MR Analysis**: Performing comprehensive Mendelian Randomization studies
4. **Report Generation**: Creating detailed analysis reports with statistical results and visualizations

## Project Structure

### Core Components

```
src/
├── mragent/                    # Main package directory
│   ├── __init__.py            # Package initialization
│   ├── agent_workflow.py      # Main MRAgent class (1038 lines)
│   ├── agent_workflow_OE.py   # Outcome-Exposure specific workflow
│   ├── agent_tool.py          # Core tools and utilities (709 lines)
│   ├── LLM.py                 # LLM integration (OpenAI, Ollama)
│   └── template_text.py       # LLM prompt templates (219 lines)
├── agent_workflow_demo.py     # Knowledge Discovery mode demo
├── agent_workflow_OE_demo.py  # Causal Validation mode demo
├── web_demo.py               # Streamlit web interface
└── test files                # Various evaluation scripts
```

### Training Data Structure

```
datatrain/
├── parasite-ids-390/         # Parasite-related disease data (390 diseases)
├── bacteria-ids-4937/        # Bacterial disease data (4937 diseases)  
├── fugus-ids-610/           # Fungal disease data (610 diseases)
└── microorganism-ids-8228/   # General microorganism data (8228 diseases)
```

Each category contains Excel files organized alphabetically by disease name, suggesting this is training/reference data for medical conditions and their associations.

## Architecture Design

### 1. Agent Workflow System

#### Two Operation Modes:

**Knowledge Discovery Mode (`MRAgent`)**:
- Input: Single disease name
- Process: Automatically discovers potential exposures/outcomes
- Output: Comprehensive analysis of all discovered relationships

**Causal Validation Mode (`MRAgentOE`)**:
- Input: Specific exposure-outcome pair
- Process: Direct validation of the causal relationship
- Output: Focused analysis report

#### 9-Step Workflow Pipeline:

1. **Literature Scanning**: PubMed article retrieval and analysis
2. **MR History Check**: Verify if relationships have been previously studied
3. **Synonym Expansion**: Medical terminology enrichment via UMLS
4. **GWAS Availability**: Check OpenGWAS database for genetic data
5. **GWAS ID Selection**: AI-powered selection of relevant genetic studies
6. **Cartesian Product**: Generate all possible exposure-outcome combinations
7. **MR Feasibility**: Final validation of analysis readiness
8. **Pair Selection**: Choose optimal combinations for analysis
9. **MR Execution**: Perform analysis and generate reports

### 2. LLM Integration Layer

**Supported Models**:
- OpenAI GPT (gpt-4o, gpt-3.5-turbo, etc.)
- Local models via Ollama
- Compatible with any OpenAI API-compatible service

**Template System**: Structured prompts for different tasks:
- Literature analysis
- Relationship extraction
- GWAS selection
- Result interpretation
- Report generation

### 3. Data Integration Components

**External APIs**:
- **PubMed/Entrez**: Scientific literature retrieval
- **OpenGWAS**: Genetic association data access
- **UMLS**: Medical terminology and synonyms

**R Integration**: 
- TwoSampleMR package for MR analysis
- MRlap for sample overlap correction
- Statistical visualization generation

### 4. Analysis Engine

**MR Methods Supported**:
- Classical Mendelian Randomization (`MR`)
- Mixture of Experts approach (`MR_MOE`)
- Sample overlap correction (MRlap)
- Quality evaluation via STROBE-MR guidelines

**Output Generation**:
- Statistical results (CSV files)
- Visualization plots (PDF)
- Comprehensive reports (PDF)
- Quality assessments

## Key Technical Features

### 1. Intelligent Literature Processing
- Automated PubMed querying with configurable parameters
- LLM-powered extraction of exposure-outcome relationships
- Quality filtering and relevance scoring

### 2. Genetic Data Management
- Integration with OpenGWAS database (8,000+ studies)
- Population stratification handling
- Automated GWAS selection based on relevance and quality

### 3. Statistical Robustness
- Multiple MR methods for validation
- Heterogeneity and pleiotropy testing
- Sensitivity analyses (leave-one-out, funnel plots)
- Sample overlap detection and correction

### 4. Quality Assurance
- STROBE-MR guideline compliance checking
- Bidirectional analysis support
- Comprehensive sensitivity testing
- Automated report generation with statistical interpretation

## Configuration Options

### Core Parameters:
- **Mode**: 'O' (outcome-focused), 'E' (exposure-focused), 'OE' (direct pair)
- **LLM Model**: Configurable AI model selection
- **Analysis Depth**: Number of papers to analyze (default: 100)
- **MR Method**: Classical or mixture-of-experts approach
- **Quality Controls**: STROBE-MR evaluation, sample overlap correction

### Advanced Features:
- Bidirectional analysis
- Synonym expansion via UMLS
- Introduction generation
- Multiple population support
- Custom API endpoints

## Output Structure

```
output/
└── [Disease]_[Model]/
    ├── Exposure_and_Outcome.csv    # Discovered relationships
    ├── Outcome_SNP.csv             # Genetic data availability
    ├── mr_run.csv                  # Selected analysis pairs
    └── [Exposure]_[Outcome]/       # Individual analysis results
        ├── MR_[ID1]_[ID2]/         # Per-GWAS-pair results
        │   ├── table.MRresult.csv  # Statistical results
        │   ├── *.pdf               # Visualization plots
        │   └── LLM_result.txt      # AI interpretation
        ├── Introduction.pdf         # Background information
        └── Conclusion.pdf          # Summary report
```

## Technology Stack

- **Core**: Python 3.9+
- **Statistical Analysis**: R 4.3.4+ with specialized packages
- **AI/ML**: OpenAI API, Ollama for local models
- **Data Processing**: pandas, BioPython
- **Visualization**: R plotting libraries, ReportLab for PDFs
- **Web Interface**: Streamlit
- **External APIs**: PubMed/Entrez, OpenGWAS, UMLS

## Research Applications

### Primary Use Cases:
1. **Exploratory Research**: Discover unknown causal relationships
2. **Hypothesis Validation**: Test specific exposure-outcome hypotheses  
3. **Literature Gap Analysis**: Identify under-researched areas
4. **Clinical Decision Support**: Evidence-based causal inference

### Target Users:
- Medical researchers
- Epidemiologists  
- Clinicians
- Public health professionals
- Bioinformatics specialists

## Innovation Aspects

1. **Automated Discovery**: First system to fully automate the MR discovery pipeline
2. **AI-Powered Analysis**: LLM integration for intelligent literature processing
3. **Comprehensive Validation**: Multi-method statistical approach with quality controls
4. **User-Friendly Interface**: Both programmatic and web-based access
5. **Reproducible Research**: Standardized methodology with detailed reporting

This architecture represents a significant advancement in automated causal inference for medical research, combining the power of AI with rigorous statistical methods to accelerate scientific discovery in disease causation. 