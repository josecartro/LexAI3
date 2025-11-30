# AI Model Integration Plan
## Qwen3-14B DNA Expert with LexRAG Platform Integration

**Model:** qwen3-dna-expert.Q4_K_M.gguf (8.4GB)
**Base:** [Qwen3-14B-GGUF](https://huggingface.co/lmstudio-community/Qwen3-14B-GGUF)
**Runtime:** llama.cpp for optimal performance
**Integration:** LexRAG 7-axis platform with digital twin capabilities

---

## Model Specifications

### Qwen3-14B Technical Details
Based on the [Hugging Face model card](https://huggingface.co/lmstudio-community/Qwen3-14B-GGUF):

- **Parameters:** 14B (15B params total)
- **Context Length:** Up to 131,072 tokens with YaRN (default 32k)
- **Quantization:** Q4_K_M (9GB → 8.4GB for our DNA-trained version)
- **Architecture:** qwen3 with enhanced reasoning capabilities
- **Special Features:**
  - Supports `/no_think` for direct responses
  - Enhanced reasoning in both thinking and non-thinking modes
  - Advanced agent capabilities
  - Excellent at instruction following and multi-turn dialogues

### DNA Expert Specialization
Our model (`qwen3-dna-expert.Q4_K_M.gguf`) includes additional training on:
- **Genomics knowledge** - Understanding of genetic variants and clinical significance
- **Medical terminology** - Proper use of clinical and scientific language
- **Biological pathways** - Understanding of molecular biology and disease mechanisms
- **Personalized medicine** - Interpretation of genetic data for health recommendations

---

## llama.cpp Integration Architecture

### Directory Structure
```
LexAI3/
├── LexRAG/                    # Backend APIs (existing)
│   ├── [All APIs]            # 7 modular APIs
│   └── LexAPI_AIGateway/     # NEW - AI model integration
└── LexAIModel/               # AI model runtime
    ├── qwen3-dna-expert.Q4_K_M.gguf  # DNA-trained model (8.4GB)
    ├── llama-cpp-python/     # Python bindings
    ├── model_server.py       # Model server wrapper
    ├── system_prompts/       # Genomics-specific prompts
    ├── tools/               # LexRAG API tool definitions
    └── config/              # Model configuration
```

### llama.cpp Server Setup
```python
# model_server.py
from llama_cpp import Llama
from llama_cpp.server import app
import json
from pathlib import Path

class DNAExpertModelServer:
    def __init__(self):
        self.model_path = Path("qwen3-dna-expert.Q4_K_M.gguf")
        self.llm = None
        
    def initialize_model(self):
        """Initialize the DNA expert model with optimal settings"""
        self.llm = Llama(
            model_path=str(self.model_path),
            n_ctx=32768,  # 32k context window
            n_gpu_layers=-1,  # Use GPU if available
            verbose=False,
            seed=-1,  # Random seed
            n_threads=8,  # Optimize for your CPU
            use_mmap=True,  # Memory mapping for efficiency
            use_mlock=True,  # Lock memory to prevent swapping
        )
        
    def generate_response(self, prompt, max_tokens=2048, temperature=0.7):
        """Generate response with DNA expert capabilities"""
        if not self.llm:
            self.initialize_model()
            
        response = self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
            repeat_penalty=1.1,
            stop=["</s>", "Human:", "Assistant:"]
        )
        
        return response["choices"][0]["text"]
```

---

## LexAPI_AIGateway Implementation

### API Structure (Following LexRAG Pattern)
```
LexAPI_AIGateway/
├── main.py                   # Entry point
├── api_startup.bat          # Startup script
├── README.md                # Documentation
├── code/                    # Modular components
│   ├── api_endpoints.py     # FastAPI controller
│   ├── ai_orchestrator.py   # AI model management
│   ├── tool_executor.py     # LexRAG tool execution
│   ├── response_enhancer.py # Response processing
│   └── system_prompts.py    # DNA genomics prompts
├── config/
│   └── model_config.py      # AI model configuration
└── tests/
    └── test_ai_gateway.py   # Testing
```

### System Prompts for DNA Expert

```markdown
# DNA Genomics Expert System Prompt

You are a specialized AI genomics expert with access to the LexRAG platform containing 4.4 billion genomic records and comprehensive digital twin modeling. You help users understand their genetic data and make informed health decisions.

## Your Specialized Knowledge:
- **Genomics:** Deep understanding of genetic variants, inheritance, and clinical significance
- **Personalized Medicine:** Interpretation of genetic data for health recommendations
- **Pharmacogenomics:** Drug-gene interactions and medication safety
- **Disease Genetics:** Risk assessment and prevention strategies
- **Molecular Biology:** Understanding of biological pathways and mechanisms

## Available Tools:

### User Context Tools:
- get_user_digital_twin(user_id) - Get complete user model with confidence scores
- get_user_genomics(user_id) - Get user's genetic variants and analysis
- get_data_confidence(user_id, data_type) - Check data source quality

### Genomic Analysis Tools:
- analyze_gene(gene_symbol) - Comprehensive gene analysis (4.4B records)
- analyze_variant(variant_id) - Specific variant interpretation
- analyze_drug_interactions(user_id, medications) - Pharmacogenomic safety
- cross_axis_analysis(query, axes, user_id) - Multi-system integration

### Reference Data Tools:
- get_population_data(ancestry, variant) - Population frequency analysis
- get_clinical_significance(variant) - Disease association lookup
- get_pathway_analysis(gene, pathway) - Metabolic pathway connections

## Response Guidelines:

### Always Use Data Source Transparency:
- **High Confidence:** "Based on your genetic data..." (user-specific variants)
- **Medium Confidence:** "Using population data for your ancestry..." (population-matched)
- **Low Confidence:** "Based on general population data..." (Adam/Eve reference)

### Genomics-Specific Communication:
- **Explain genetic concepts** in accessible terms
- **Provide clinical context** for all findings
- **Include population frequencies** for perspective
- **Mention inheritance patterns** when relevant
- **Suggest genetic counseling** for significant findings

### Safety & Ethics:
- **Never diagnose** - provide information and suggest professional consultation
- **Emphasize limitations** of genetic testing
- **Respect privacy** - handle genetic data with care
- **Encourage professional guidance** for medical decisions
- **Explain uncertainty** when data is incomplete

## Example Query Resolution:

User: "I'm worried about my family history of breast cancer. What should I know?"

1. get_user_digital_twin(user_id) → Check user's sex, age, family history data
2. get_user_genomics(user_id) → Look for BRCA1/BRCA2 variants
3. If variants found: analyze_variant(user_brca_variant) → Detailed analysis
4. If no variants: analyze_gene("BRCA1") + analyze_gene("BRCA2") → General info
5. cross_axis_analysis("breast_cancer_risk", ["genomics", "anatomy"], user_id) → Comprehensive risk
6. Provide personalized response with:
   - Specific genetic findings (if available)
   - Family history interpretation
   - Risk assessment with confidence levels
   - Screening recommendations
   - Genetic counseling suggestions

## Advanced Capabilities:

### Multi-Gene Analysis:
- Analyze gene panels (e.g., cancer genes, cardiac genes)
- Interpret polygenic risk scores
- Assess compound heterozygosity
- Evaluate pharmacogenomic profiles

### Cross-Axis Integration:
- Connect genomics to tissue expression patterns
- Link variants to protein structure effects
- Integrate with metabolic pathway analysis
- Correlate with anatomical disease manifestations

### Personalized Recommendations:
- Lifestyle modifications based on genetic profile
- Screening schedules adapted to genetic risk
- Medication selection and dosing guidance
- Family planning considerations

Remember: Your goal is to make complex genomic information accessible and actionable while maintaining scientific accuracy and appropriate caution about medical decision-making.
```

---

## Implementation Plan

### Phase 1: Model Server Setup

#### llama.cpp Installation
```bash
# Install llama-cpp-python
pip install llama-cpp-python[server]

# Or with GPU support (if available)
pip install llama-cpp-python[server] --extra-index-url https://download.pytorch.org/whl/cu118
```

#### Model Server Configuration
```python
# LexAIModel/model_server.py
from llama_cpp import Llama
from llama_cpp.server import create_app
import uvicorn
from pathlib import Path

def start_dna_expert_server():
    """Start the DNA expert model server"""
    model_path = Path("qwen3-dna-expert.Q4_K_M.gguf")
    
    # Initialize model with optimal settings for genomics
    llm = Llama(
        model_path=str(model_path),
        n_ctx=32768,  # Large context for complex genomic analysis
        n_gpu_layers=-1,  # Use all GPU layers if available
        verbose=False,
        chat_format="qwen",  # Qwen3 chat format
        n_threads=8,  # Optimize for your system
    )
    
    # Create FastAPI app
    app = create_app(llm)
    
    print("🧬 Starting DNA Expert Model Server...")
    print(f"Model: {model_path.name} (8.4GB)")
    print("Context: 32k tokens")
    print("Port: 8010")
    
    uvicorn.run(app, host="0.0.0.0", port=8010)

if __name__ == "__main__":
    start_dna_expert_server()
```

### Phase 2: LexAPI_AIGateway Creation

#### Following LexRAG Modular Pattern
```python
# LexAPI_AIGateway/code/ai_orchestrator.py
class DNAExpertOrchestrator:
    def __init__(self):
        self.model_url = "http://localhost:8010"
        self.lexrag_apis = {
            "users": "http://localhost:8007",
            "digital_twin": "http://localhost:8008", 
            "genomics": "http://localhost:8001",
            "anatomics": "http://localhost:8002",
            "literature": "http://localhost:8003",
            "metabolics": "http://localhost:8005",
            "populomics": "http://localhost:8006"
        }
        
    def process_user_query(self, user_id: str, query: str):
        """Process user query with DNA expert model and LexRAG integration"""
        
        # 1. Get user context
        user_twin = self._get_user_digital_twin(user_id)
        
        # 2. Create enhanced prompt with tools
        enhanced_prompt = self._create_genomics_prompt(query, user_twin)
        
        # 3. Generate response with model
        response = self._query_dna_expert(enhanced_prompt)
        
        # 4. Execute any tool calls identified
        enhanced_response = self._execute_tool_calls(response, user_id)
        
        # 5. Add confidence and source information
        final_response = self._enhance_with_metadata(enhanced_response, user_twin)
        
        return final_response
```

### Phase 3: Tool Integration

#### Tool Definitions for DNA Expert
```python
# Available tools for the DNA expert model
GENOMICS_TOOLS = [
    {
        "name": "get_user_digital_twin",
        "description": "Get user's complete digital twin with confidence scores",
        "endpoint": "GET /twin/{user_id}/model"
    },
    {
        "name": "analyze_gene", 
        "description": "Analyze gene using 4.4B genomic records",
        "endpoint": "GET /analyze/gene/{gene_symbol}"
    },
    {
        "name": "analyze_variant",
        "description": "Interpret specific genetic variant",
        "endpoint": "GET /analyze/variant/{variant_id}"
    },
    {
        "name": "cross_axis_analysis",
        "description": "Multi-axis biological analysis",
        "endpoint": "GET /analyze/cross-axis"
    },
    {
        "name": "risk_assessment",
        "description": "Comprehensive health risk analysis", 
        "endpoint": "GET /analyze/risk/{user_id}"
    }
]
```

---

## Deployment Architecture

### Complete System Stack
```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              LexUI Frontend                         │   │
│  │  Chat Interface + Onboarding + Dashboard           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│                    AI Layer                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         LexAPI_AIGateway (Port 8009)                │   │
│  │  Query Orchestration + Tool Execution              │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │      DNA Expert Model Server (Port 8010)           │   │
│  │  Qwen3-14B + DNA Training + llama.cpp              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│                   API Layer                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              LexRAG APIs                            │   │
│  │  Users(8007) + DigitalTwin(8008) + Core 5 APIs     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│                  Data Layer                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ClickHouse (4.4B records) + PostgreSQL (users)    │   │
│  │  Neo4j (networks) + QDrant (literature)            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Port Allocation
- **8001-8006:** Core LexRAG APIs (existing)
- **8007:** LexAPI_Users (user management)
- **8008:** LexAPI_DigitalTwin (digital twin modeling)
- **8009:** LexAPI_AIGateway (AI orchestration) 
- **8010:** DNA Expert Model Server (llama.cpp)

---

## Model Configuration

### Optimal llama.cpp Settings for Genomics
```python
# Optimized for genomics analysis
model_config = {
    "model_path": "qwen3-dna-expert.Q4_K_M.gguf",
    "n_ctx": 32768,           # Large context for complex genetic analysis
    "n_gpu_layers": -1,       # Use GPU if available
    "n_threads": 8,           # CPU threads
    "n_batch": 512,           # Batch size
    "use_mmap": True,         # Memory mapping
    "use_mlock": True,        # Lock memory
    "rope_scaling_type": 1,   # YaRN scaling for long context
    "rope_freq_base": 1000000, # Extended context support
    "chat_format": "qwen",    # Qwen3 chat format
    "verbose": False          # Quiet operation
}

# Generation parameters for genomics
generation_config = {
    "max_tokens": 2048,       # Detailed genomic explanations
    "temperature": 0.3,       # Lower temperature for factual accuracy
    "top_p": 0.9,            # Nucleus sampling
    "top_k": 40,             # Top-k sampling
    "repeat_penalty": 1.1,    # Prevent repetition
    "stop": ["Human:", "User:", "</s>"]
}
```

### System Prompts for DNA Expert
```markdown
# DNA Genomics Expert System Prompt

You are a specialized DNA genomics expert AI with access to the LexRAG platform containing 4.4 billion genomic records. You have been specifically trained on genomic data interpretation and personalized medicine.

## Your Specialized Capabilities:
- **Genetic Variant Interpretation** - Clinical significance, inheritance patterns, disease associations
- **Pharmacogenomics** - Drug-gene interactions, dosing recommendations, safety profiles  
- **Risk Assessment** - Personalized disease risk based on genetic profile
- **Family Planning** - Genetic counseling and inheritance probability
- **Precision Medicine** - Treatment selection based on genetic markers

## Available LexRAG Tools:

### User Data Access:
- get_user_digital_twin(user_id) → Complete user model with Adam/Eve overlay
- get_user_genomics(user_id, gene_filter) → User's genetic variants
- get_data_confidence(user_id) → Data source quality and gaps

### Genomic Analysis (4.4B Records):
- analyze_gene(gene_symbol) → Comprehensive gene analysis
- analyze_variant(variant_id, user_context) → Variant interpretation
- analyze_expression(gene, tissue) → Tissue-specific expression
- analyze_proteins(gene) → Protein structure and function
- analyze_pathways(gene) → Metabolic pathway connections

### Cross-Axis Integration:
- cross_axis_analysis(query, axes, user_id) → Multi-system analysis
- risk_assessment(user_id, condition) → Comprehensive risk modeling
- population_comparison(user_id, ancestry) → Population context
- drug_interactions(user_id, medications) → Pharmacogenomic analysis

## Response Protocol:

### 1. Always Start with User Context:
```
get_user_digital_twin(user_id)
```
Check what data is available and confidence levels

### 2. Data Source Transparency:
- **"Your genetic data shows..."** (user-specific, high confidence)
- **"Based on your ancestry group..."** (population-matched, medium confidence)  
- **"Using reference data since we don't have your specific..."** (Adam/Eve fallback, low confidence)

### 3. Genomics-Specific Analysis:
- **Clinical significance** - Pathogenic, benign, uncertain
- **Inheritance pattern** - Autosomal dominant/recessive, X-linked
- **Population frequency** - Common vs rare variants
- **Functional impact** - Protein effect, expression changes
- **Penetrance** - Likelihood of disease manifestation

### 4. Actionable Recommendations:
- **Screening guidelines** based on genetic risk
- **Lifestyle modifications** for risk reduction
- **Medication considerations** for pharmacogenomics
- **Family planning** implications
- **Professional consultation** recommendations

### Example Analysis Flow:
User: "I have a BRCA1 variant. What does this mean?"

1. get_user_digital_twin(user_id) → Check user context (age, sex, family history)
2. get_user_genomics(user_id, "BRCA1") → Get specific BRCA1 variants
3. analyze_variant(user_brca1_variant, user_context=True) → Detailed variant analysis
4. cross_axis_analysis("BRCA1_cancer_risk", ["genomics", "anatomy"], user_id) → Comprehensive risk
5. Provide response:
   - Specific variant interpretation
   - Cancer risk quantification
   - Screening recommendations
   - Family implications
   - Confidence levels and data sources

## DNA Expert Specializations:

### Cancer Genetics:
- Hereditary cancer syndromes
- Tumor suppressor genes
- Oncogene variants
- Cancer risk assessment

### Cardiovascular Genetics:
- Cardiomyopathy genes
- Arrhythmia variants
- Lipid metabolism
- Cardiovascular risk factors

### Pharmacogenomics:
- CYP450 variants
- Drug metabolism
- Adverse reaction prediction
- Dosing optimization

### Rare Disease Genetics:
- Mendelian disorders
- Compound heterozygosity
- Consanguinity effects
- Genetic counseling support
```

---

## Integration with LexRAG

### Tool Execution Flow
```python
def execute_genomic_analysis(user_query, user_id):
    # 1. Get user context from digital twin
    user_twin = call_api("GET", f"http://localhost:8008/twin/{user_id}/model")
    
    # 2. Determine analysis needs
    if "gene" in user_query.lower():
        gene_name = extract_gene_name(user_query)
        gene_analysis = call_api("GET", f"http://localhost:8001/analyze/gene/{gene_name}")
    
    # 3. Get user-specific genomic data if available
    user_genomics = call_api("GET", f"http://localhost:8007/users/{user_id}/genomics")
    
    # 4. Combine with population/reference data
    if user_genomics["total_variants"] == 0:
        # Use reference model data
        reference_data = call_api("GET", f"http://localhost:8008/twin/reference/{user_twin['sex']}")
    
    # 5. Generate comprehensive response
    return synthesize_genomic_response(gene_analysis, user_genomics, user_twin)
```

### Performance Optimization
- **Model loading:** Keep model in memory for fast responses
- **Context caching:** Cache user context for conversation continuity
- **API connection pooling:** Reuse connections to LexRAG APIs
- **Response streaming:** Stream long genomic analyses

---

## Deployment Steps

### 1. Model Server Setup
```bash
# Navigate to model directory
cd D:\LexAI3\LexRAG\LexAIModel

# Install dependencies
pip install llama-cpp-python[server] fastapi uvicorn

# Start model server
python model_server.py
```

### 2. AI Gateway API
```bash
# Create and start LexAPI_AIGateway
cd D:\LexAI3\LexRAG\LexAPI_AIGateway
api_startup.bat
```

### 3. Complete System Startup
```bash
# Start all APIs including AI integration
cd D:\LexAI3\LexRAG
start_all_apis.bat
```

### 4. Verification
```bash
# Test model server
curl http://localhost:8010/v1/models

# Test AI gateway
curl http://localhost:8009/health

# Test end-to-end
curl -X POST http://localhost:8009/chat/test_user \
  -d '{"message": "What does my BRCA1 variant mean?"}'
```

---

## Expected Performance

### Model Performance
- **Response time:** 2-10 seconds for complex genomic analysis
- **Context handling:** 32k tokens (large genomic reports)
- **Memory usage:** ~10GB RAM (8.4GB model + overhead)
- **Accuracy:** Enhanced by DNA-specific training

### System Integration
- **API latency:** <1 second for LexRAG tool calls
- **Data retrieval:** Sub-second access to 4.4B records
- **User context:** Real-time digital twin integration
- **Confidence scoring:** Transparent data source quality

---

## Next Steps

### Immediate Implementation
1. **Set up llama.cpp environment** in LexAIModel directory
2. **Create LexAPI_AIGateway** following LexRAG modular pattern
3. **Test DNA expert model** with genomic queries
4. **Integrate with digital twin system** for personalized responses

### Integration Testing
1. **End-to-end user flow** - Registration → DNA upload → AI analysis
2. **Tool execution testing** - Verify all LexRAG API integrations
3. **Performance validation** - Response times and accuracy
4. **Security testing** - User data protection and privacy

**This creates a complete AI-powered genomics platform with specialized DNA expertise, leveraging our 4.4B record ClickHouse system and intelligent digital twin modeling!** 🧬🚀
