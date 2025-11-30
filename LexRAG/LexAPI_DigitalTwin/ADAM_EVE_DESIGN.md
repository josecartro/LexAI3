# Adam & Eve Genetic Reference Models
## Intelligent Fallback Data for User Analysis

### Design Principle
**Adam & Eve provide population-typical data for any missing user information, enabling complete analysis even with partial user data.**

---

## Adam - Default Male Reference

### Core Demographics
```json
{
  "age_years": 35,
  "height_cm": 175,
  "weight_kg": 75,
  "bmi": 24.5,
  "ancestry": "mixed_european"
}
```

### Genetic Baseline (Population Typical)
```json
{
  "pharmacogenomics": {
    "CYP2D6": "*1/*1",          // Normal metabolizer (77% population)
    "CYP2C19": "*1/*1",         // Normal metabolizer (70% population)  
    "CYP3A4": "*1/*1",          // Normal activity
    "DPYD": "*1/*1",            // Normal DPD activity
    "TPMT": "*1/*1",            // Normal TPMT activity
    "phenotype": "typical_metabolizer"
  },
  "disease_genetics": {
    "APOE": "ε3/ε3",            // Most common (77% population)
    "BRCA1": "wild_type",       // No pathogenic variants (99.8%)
    "BRCA2": "wild_type",       // No pathogenic variants (99.8%)
    "TP53": "wild_type",        // No pathogenic variants (99.9%)
    "CFTR": "wild_type",        // No CF variants (99.96%)
    "cardiac_genes": "low_risk" // No major cardiac variants
  },
  "population_frequencies": {
    "common_variants": "population_average_male",
    "rare_variants": "none_assumed",
    "ancestry_markers": "mixed_european_typical"
  }
}
```

### Health Baseline
```json
{
  "family_history": {
    "cardiovascular": "average_risk",    // No strong family history
    "cancer": "average_risk",            // Population baseline
    "diabetes": "average_risk",
    "alzheimers": "average_risk"
  },
  "lifestyle": {
    "exercise": "moderate_3x_week",      // Population average
    "diet": "standard_western",          // Typical diet
    "smoking": "never",                  // Assume never smoker
    "alcohol": "moderate",               // 1-2 drinks/week
    "sleep": "7_hours_regular"
  },
  "current_health": {
    "chronic_conditions": [],            // Assume healthy
    "medications": [],                   // No current medications
    "allergies": [],                     // No known allergies
    "bmi_category": "normal"
  }
}
```

---

## Eve - Default Female Reference

### Core Demographics
```json
{
  "age_years": 32,
  "height_cm": 162,
  "weight_kg": 65,
  "bmi": 24.7,
  "ancestry": "mixed_european"
}
```

### Genetic Baseline (Female-Specific)
```json
{
  "pharmacogenomics": {
    "CYP2D6": "*1/*1",          // Normal metabolizer
    "CYP2C19": "*1/*1",         // Normal metabolizer
    "hormonal_variants": "typical_premenopausal"
  },
  "disease_genetics": {
    "APOE": "ε3/ε3",            // Most common
    "BRCA1": "wild_type",       // No pathogenic variants
    "BRCA2": "wild_type",       // No pathogenic variants
    "TP53": "wild_type",        // No pathogenic variants
    "reproductive_genes": "low_risk"
  },
  "female_specific": {
    "estrogen_receptor": "normal",
    "progesterone_receptor": "normal",
    "hormone_metabolism": "typical"
  }
}
```

### Reproductive Health Baseline
```json
{
  "menstrual_cycle": {
    "cycle_length": 28,
    "regularity": "regular",
    "age_at_menarche": 13
  },
  "reproductive_status": {
    "pregnancies": 0,           // Nulliparous baseline
    "contraception": "none",
    "fertility_status": "normal"
  }
}
```

---

## Usage Examples

### Example 1: Incomplete User Data
```
User Data Available:
- Age: 40, Sex: Male
- DNA: Only APOE ε4/ε4 variant

Adam Provides:
- All other genetic variants (CYP2D6 *1/*1, BRCA1 wild-type, etc.)
- Family history (average risk)
- Lifestyle (moderate exercise, standard diet)

AI Response:
"Based on your APOE ε4/ε4 variant (high Alzheimer's risk) and assuming 
population-typical genetics for other genes since we don't have your 
complete genetic data..."
```

### Example 2: User with Family History
```
User Data Available:
- Demographics: 45yo female
- Family History: Breast cancer (mother, sister)
- No genetic testing

Eve Provides:
- Genetic variants (BRCA1/2 wild-type assumption)
- Lifestyle defaults
- Other family history

AI Response:
"Given your strong family history of breast cancer, even though we're 
assuming typical BRCA1/2 genes (since no genetic testing available), 
your risk is elevated and genetic testing is recommended..."
```

### Example 3: Pharmacogenomics Query
```
User Data Available:
- Basic demographics
- No pharmacogenomic testing

Adam/Eve Provides:
- CYP2D6 *1/*1 (normal metabolizer assumption)
- Other drug metabolism genes

AI Response:
"Assuming typical drug metabolism genes (since no pharmacogenomic 
testing available), most medications should work at standard doses, 
but genetic testing could provide personalized dosing..."
```

---

## Implementation Strategy

### Data Sources for Baselines
1. **gnomAD Population Data** - Use our 17.6M variants for frequency baselines
2. **ClinVar Data** - Use our 3.68M variants for disease risk baselines  
3. **GTEx Expression** - Use our 484M records for tissue expression baselines
4. **Pharmacogenomic Data** - Use population frequencies for drug metabolism

### Transparency in AI Responses
- **"Your genetic data shows..."** (user-specific, high confidence)
- **"Based on your [partial data] and population averages..."** (mixed confidence)
- **"Assuming typical genetics since no testing available..."** (low confidence, Adam/Eve)

### Dynamic Data Collection
```
AI: "I notice you don't have pharmacogenomic data. Would you like to:
1. Get genetic testing for personalized medication guidance
2. Answer questions about drug responses you've experienced  
3. Continue with population-average assumptions"
```

**Should I redesign the Adam & Eve models to include these comprehensive genetic baselines using our actual population data from the 4.4B record database?**

This would create true **genetic reference humans** rather than just demographic templates.
