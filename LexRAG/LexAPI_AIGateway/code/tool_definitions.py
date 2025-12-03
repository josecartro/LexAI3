"""
OpenAI-Compatible Tool Definitions for LM Studio Function Calling
Defines all available tools that the DNA Expert AI can use
"""

# All tools in OpenAI function calling format
LEXRAG_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_user_digital_twin",
            "description": "Get the user's complete digital twin model with genomic data, demographics, and confidence scores. Always call this first to understand the user's data completeness.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user's identifier"
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_gene",
            "description": "Analyze a specific gene using the 4.4 billion genomic record database. Returns comprehensive analysis including variants, clinical significance, tissue expression, and protein connections.",
            "parameters": {
                "type": "object",
                "properties": {
                    "gene_symbol": {
                        "type": "string",
                        "description": "Official gene symbol (e.g., BRCA1, TP53, APOE, MLH1)"
                    }
                },
                "required": ["gene_symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_variant",
            "description": "Analyze a specific genetic variant (SNP or mutation) using the genomic database. Returns clinical significance, population frequencies, and disease associations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "variant_id": {
                        "type": "string",
                        "description": "Variant identifier (rsID like rs7412, or genomic coordinate)"
                    }
                },
                "required": ["variant_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_genomics",
            "description": "Retrieve the user's personal genomic data from their uploaded DNA file. Use this to see what actual variants the user has.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user's identifier"
                    },
                    "gene_filter": {
                        "type": "string",
                        "description": "Optional gene symbol to filter results (e.g., BRCA1)"
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_organ",
            "description": "Analyze anatomical structures and organs using the Neo4j anatomical database. Returns structure information, gene connections, and tissue relationships.",
            "parameters": {
                "type": "object",
                "properties": {
                    "organ_name": {
                        "type": "string",
                        "description": "Organ or anatomical structure name (e.g., heart, brain, shoulder, liver)"
                    }
                },
                "required": ["organ_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_literature",
            "description": "Search medical and scientific literature using the QDrant vector database. Returns relevant research papers and medical knowledge about a topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Research topic or medical condition to search for (e.g., 'Lynch syndrome', 'cervical radiculopathy')"
                    }
                },
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_metabolic_profile",
            "description": "Get metabolic pathway analysis and biochemical profile for a user based on their genetic variants.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user's identifier"
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_drug_metabolism",
            "description": "Analyze how a specific drug is metabolized, including CYP450 enzyme interactions and pharmacogenomic considerations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "drug_name": {
                        "type": "string",
                        "description": "Drug name (generic or brand name)"
                    }
                },
                "required": ["drug_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_environmental_risk",
            "description": "Get environmental health risk factors for a specific geographic location, including pollutants, allergens, and environmental exposures.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Geographic location (city, region, or country)"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_disease_risk",
            "description": "Get population-level disease risk data and genetic associations for a specific disease or condition.",
            "parameters": {
                "type": "object",
                "properties": {
                    "disease": {
                        "type": "string",
                        "description": "Disease or condition name (e.g., 'breast cancer', 'Lynch syndrome', 'type 2 diabetes')"
                    }
                },
                "required": ["disease"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_drug_interactions",
            "description": "Analyze pharmacogenomic drug interactions for a user based on their CYP450 and other drug metabolism genes. Returns personalized medication guidance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user's identifier"
                    },
                    "medications": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of medication names to analyze"
                    }
                },
                "required": ["user_id", "medications"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "risk_assessment",
            "description": "Perform comprehensive health risk assessment for a user across multiple genetic and environmental factors. Use when user asks about overall health risks or specific conditions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user's identifier"
                    },
                    "condition": {
                        "type": "string",
                        "description": "Optional specific condition to assess (e.g., 'cardiovascular', 'cancer', 'alzheimer')"
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cross_axis_analysis",
            "description": "Perform integrated analysis across multiple biological systems (genomics, anatomy, literature, metabolics, etc.). Use for complex questions requiring multi-system integration.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The analysis question or topic"
                    },
                    "axes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Biological axes to analyze: 'genomics', 'anatomy', 'literature', 'metabolics', 'populomics'"
                    }
                },
                "required": ["query", "axes"]
            }
        }
    },
    # ============== NEW HIGH-VALUE TOOLS ==============
    {
        "type": "function",
        "function": {
            "name": "analyze_splice_impact",
            "description": "Analyze splice site impact for a gene or variant. Returns transcript-specific SpliceAI predictions, GTEx tissue dominance for each transcript, and anatomy mappings. Essential for understanding tissue-specific disease manifestation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "gene_or_variant": {
                        "type": "string",
                        "description": "Gene symbol (e.g., BRCA1) or variant ID (e.g., rs123456)"
                    }
                },
                "required": ["gene_or_variant"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "phenotype_to_differential",
            "description": "Map phenotypes (HPO terms or symptoms) to candidate diseases, implicated genes, and anatomy focus. Use for syndrome identification and differential diagnosis. Returns ranked MONDO diseases with supporting evidence.",
            "parameters": {
                "type": "object",
                "properties": {
                    "phenotypes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of HPO terms (e.g., 'HP:0001250') or symptom descriptions (e.g., 'seizures', 'hypotonia')"
                    }
                },
                "required": ["phenotypes"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_regulatory_variant",
            "description": "Interpret non-coding/regulatory variants using ENCODE data. Returns overlapping regulatory elements (enhancers, promoters), target genes with confidence scores, expression impact by tissue, and phenotype priors via MONDO/HPO.",
            "parameters": {
                "type": "object",
                "properties": {
                    "variant_id": {
                        "type": "string",
                        "description": "Variant identifier (rsID or genomic coordinate like chr1:12345:A:G)"
                    }
                },
                "required": ["variant_id"]
            }
        }
    }
]

def get_tool_definitions():
    """Get all tool definitions for LM Studio"""
    return LEXRAG_TOOLS

def get_human_readable_tool_name(tool_name: str) -> str:
    """Convert tool name to human-readable description"""
    tool_names = {
        "get_user_digital_twin": "your personal health profile",
        "analyze_gene": "genomic variant database",
        "analyze_variant": "clinical variant database",
        "get_user_genomics": "your DNA file",
        "analyze_organ": "anatomical structure database",
        "search_literature": "medical research literature",
        "get_metabolic_profile": "metabolic pathway database",
        "get_drug_metabolism": "pharmacogenomics database",
        "get_environmental_risk": "environmental health database",
        "get_disease_risk": "disease risk database",
        "analyze_drug_interactions": "drug interaction database",
        "risk_assessment": "comprehensive risk analysis system",
        "cross_axis_analysis": "multi-system integration engine",
        # New high-value tools
        "analyze_splice_impact": "splice prediction + tissue expression database",
        "phenotype_to_differential": "phenotype-to-disease differential engine",
        "analyze_regulatory_variant": "ENCODE regulatory element database"
    }
    return tool_names.get(tool_name, tool_name)

def format_tool_progress_message(tool_name: str, params: dict, user_query: str) -> str:
    """
    Generate engaging, context-aware progress messages based on tool being called
    """
    
    if tool_name == "analyze_gene":
        gene = params.get("gene_symbol", "unknown gene")
        return f"🔬 Searching 3.47 billion genomic records for {gene} variants and clinical data..."
    
    elif tool_name == "analyze_organ":
        organ = params.get("organ_name", "structure")
        return f"🫀 Looking up anatomical structure of {organ}, nerve pathways, and tissue connections..."
    
    elif tool_name == "search_literature":
        topic = params.get("topic", "topic")
        return f"📚 Searching medical research literature about {topic}..."
    
    elif tool_name == "get_user_digital_twin":
        return f"📊 Loading your personal health profile and genetic data completeness..."
    
    elif tool_name == "get_user_genomics":
        gene_filter = params.get("gene_filter")
        if gene_filter:
            return f"🧬 Retrieving your personal {gene_filter} genetic variants from uploaded DNA..."
        return f"🧬 Loading your personal genetic data from uploaded DNA file..."
    
    elif tool_name == "analyze_variant":
        variant = params.get("variant_id", "variant")
        return f"🔍 Analyzing {variant} in clinical variant database for disease associations..."
    
    elif tool_name == "get_metabolic_profile":
        return f"⚗️ Analyzing your metabolic pathways and biochemical processing..."
    
    elif tool_name == "get_drug_metabolism":
        drug = params.get("drug_name", "medication")
        return f"💊 Looking up how {drug} is metabolized by CYP450 enzymes..."
    
    elif tool_name == "analyze_drug_interactions":
        meds = params.get("medications", [])
        if meds:
            return f"⚠️ Analyzing pharmacogenomic interactions for {', '.join(meds[:3])}..."
        return f"⚠️ Analyzing drug interactions with your genetic profile..."
    
    elif tool_name == "risk_assessment":
        condition = params.get("condition", "overall health")
        return f"📈 Assessing your {condition} risk using genetic and environmental factors..."
    
    elif tool_name == "get_disease_risk":
        disease = params.get("disease", "condition")
        return f"🩺 Looking up population risk data for {disease}..."
    
    elif tool_name == "get_environmental_risk":
        location = params.get("location", "location")
        return f"🌍 Analyzing environmental health factors in {location}..."
    
    elif tool_name == "cross_axis_analysis":
        axes = params.get("axes", [])
        axes_str = ", ".join(axes) if axes else "multiple systems"
        return f"🔗 Integrating data across {axes_str} for comprehensive analysis..."
    
    # New high-value tools
    elif tool_name == "analyze_splice_impact":
        target = params.get("gene_or_variant", "target")
        return f"🧬 Analyzing splice impact for {target} across 3.43B SpliceAI predictions + GTEx tissues..."
    
    elif tool_name == "phenotype_to_differential":
        phenotypes = params.get("phenotypes", [])
        pheno_str = ", ".join(phenotypes[:3]) if phenotypes else "symptoms"
        return f"🔍 Mapping {pheno_str} to candidate diseases via HPO/MONDO ontologies..."
    
    elif tool_name == "analyze_regulatory_variant":
        variant = params.get("variant_id", "variant")
        return f"🎯 Analyzing {variant} against 1.31M ENCODE regulatory elements..."
    
    return f"🔧 Running {tool_name} analysis..."

def format_tool_complete_message(tool_name: str, params: dict, result_summary: str = "") -> str:
    """Generate completion message after tool execution"""
    
    if tool_name == "analyze_gene":
        gene = params.get("gene_symbol", "gene")
        return f"✅ Found {gene} data: variants, expression patterns, and clinical significance"
    
    elif tool_name == "analyze_organ":
        organ = params.get("organ_name", "structure")
        return f"✅ Retrieved anatomical data for {organ}"
    
    elif tool_name == "search_literature":
        return f"✅ Found relevant medical research"
    
    elif tool_name == "get_user_genomics":
        return f"✅ Loaded your personal genetic variants"
    
    # New high-value tools
    elif tool_name == "analyze_splice_impact":
        target = params.get("gene_or_variant", "target")
        return f"✅ Found splice predictions + tissue dominance for {target}"
    
    elif tool_name == "phenotype_to_differential":
        return f"✅ Mapped phenotypes to candidate diseases and genes"
    
    elif tool_name == "analyze_regulatory_variant":
        variant = params.get("variant_id", "variant")
        return f"✅ Found regulatory elements and target genes for {variant}"
    
    else:
        readable_name = get_human_readable_tool_name(tool_name)
        return f"✅ Retrieved data from {readable_name}"



