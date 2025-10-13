import json
import re
import spacy
from spacy.tokens import Span
from rapidfuzz import process
from medspacy.ner import TargetRule
from typing import Dict, List, Set
from collections import defaultdict
class MedicalNLP:
    def __init__(self):
        """Initialize the medical NLP processor with models and rules"""
        self.nlp = spacy.load("en_core_web_sm")
        print("DEBUG: SpaCy model loaded successfully")  # Debug 1
        self._setup_pipelines()
        self.diseases = self._load_disease_vocabulary()
        print(f"DEBUG: Loaded {len(self.diseases)} diseases")  # Debug 2
        self._initialize_pipelines()
        
    def _setup_pipelines(self):
        """Optional placeholder setup for additional NLP pipeline steps"""
        pass
    
    def _load_spacy_model(self):
        """Load and configure the base spaCy model"""
        nlp = spacy.load("en_core_web_sm")
        
        # Add sentence boundary detection
        nlp.add_pipe("sentencizer")
        
        # Disable unnecessary pipes for faster processing
        disable_pipes = ["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer"]
        for pipe in disable_pipes:
            if pipe in nlp.pipe_names:
                nlp.disable_pipe(pipe)
        
        return nlp

    def _initialize_pipelines(self):
        """Configure MedSpaCy pipelines with medical-specific rules"""
        # Add MedSpaCy components
        self.nlp.add_pipe("medspacy_sectionizer")
        self.nlp.add_pipe("medspacy_target_matcher")
        self.nlp.add_pipe("medspacy_context")
        
        # Add disease matching rules
        matcher = self.nlp.get_pipe("medspacy_target_matcher")
        for disease in self.diseases:
            matcher.add([TargetRule(disease, "DISEASE")])
            
        # Add additional clinical concept rules
        self._add_clinical_rules(matcher)
    
    def _normalize_disease(self, text):
        match, score = process.extractOne(text.lower(), self.diseases)
        return match if score >= 85 else text.lower()


    def _load_disease_vocabulary(self) -> Set[str]:
        """Load comprehensive disease vocabulary with breast imaging focus"""
        diseases = {
    # Breast Imaging Specific
        "BI-RADS 0", "BI-RADS 1", "BI-RADS 2", "BI-RADS 3", 
        "BI-RADS 4", "BI-RADS 5", "BI-RADS 6",
        "Ductal Carcinoma", "Lobular Carcinoma", 
        "Fibroadenoma", "Breast Cyst", "Microcalcifications",
        
    # Original Disease List (condensed for example)
        "Diabetes", "Hypertension", "COVID-19", "Pneumonia",
        "Asthma", "Rheumatoid Arthritis", "Depression",
        
    # (include all diseases from original list)
        "BI-RADS I", "BI-RADS II", "BI-RADS III", "BI-RADS IV", "BI-RADS V",
        "Ductal Carcinoma", "Lobular Carcinoma", "Fibroadenoma"
    # General Symptoms
        "Fever", "Cold", "Flu", "Sore Throat", "Cough", "Body Ache", "Fatigue", "Headache", "Nausea",
        "Vomiting", "Diarrhea", "Constipation", "Abdominal Pain", "Dizziness", "Chest Pain", "Back Pain",
        "Joint Pain", "Muscle Cramps", "Shortness of Breath", "Palpitations", "Loss of Appetite",
        "Weight Loss", "Weight Gain", "Period Pain", "Irregular Periods", "Heavy Menstrual Bleeding",
        "Vaginal Discharge", "Night Sweats", "Skin Rash", "Itching", "Nosebleeds", "Dry Mouth",
        "Sweating Excessively", "Insomnia", "Burning Sensation in Urine",
            
        # Infections & Acute Conditions
        "Viral Fever", "Dengue", "Chikungunya", "Malaria", "Typhoid", "COVID-19", "Tuberculosis", "Pneumonia",
        "Bronchitis", "Sinusitis", "Tonsillitis", "Ear Infection", "Conjunctivitis", "Strep Throat", "UTI",
        "Vaginal Yeast Infection", "Bacterial Vaginosis", "Skin Infection", "Gastroenteritis",
        "Hepatitis A", "Hepatitis B", "Hepatitis C", "HIV", "STIs", "Genital Herpes", "Scabies", "Chickenpox",
        "Measles", "Mumps", "Ringworm", "Jaundice",

        # Chronic & Systemic Diseases
        "Diabetes", "Hypertension", "Hypothyroidism", "Hyperthyroidism", "High Cholesterol", "Obesity", "PCOS",
        "Endometriosis", "Anemia", "Vitamin D Deficiency", "Vitamin B12 Deficiency", "Osteoporosis",
        "Rheumatoid Arthritis", "Osteoarthritis", "Asthma", "COPD", "Chronic Sinusitis", "GERD", "Gastritis",
        "Peptic Ulcer", "IBS", "IBD", "Crohn’s Disease", "Ulcerative Colitis", "Celiac Disease",
        "Fatty Liver Disease", "Liver Cirrhosis", "CKD", "Kidney Stones", "Gallstones", "Migraine", "Epilepsy",
        "Parkinson’s Disease", "Alzheimer’s Disease", "Multiple Sclerosis", "Lupus", "Fibromyalgia",
        "Scleroderma", "Psoriasis",

        # Cardiac, Respiratory, Neuro
        "Coronary Artery Disease", "Heart Attack", "Stroke", "Heart Failure", "Arrhythmia",
        "Atrial Fibrillation", "Anxiety Disorder", "Depression", "Panic Disorder", "PTSD", "Schizophrenia",
        "Bipolar Disorder", "ADHD", "Autism Spectrum Disorder", "Sleep Apnea",

        # Women’s Health
        "Menopause", "Hormonal Imbalance", "Infertility (Female)", "PMS", "Breast Lumps", "Ovarian Cysts",
        "Cervical Cancer", "Uterine Fibroids",

        # Men’s Health
        "Erectile Dysfunction", "Premature Ejaculation", "Infertility (Male)", "Prostate Enlargement",
        "Prostate Cancer",

        # Pediatric & Geriatric
        "Iron Deficiency in Children", "Growth Delay", "Childhood Obesity", "Bedwetting", "ADHD in Kids",
        "Autism", "Aging-Related Memory Loss", "Falls in Elderly",

        # Oncology
        "Breast Cancer", "Lung Cancer", "Colon Cancer", "Skin Cancer", "Leukemia", "Pancreatic Cancer",
        "Brain Tumor",

        # Eye, Ear, Skin
        "Cataract", "Glaucoma", "Eczema", "Dandruff"
        }
        return diseases

    def _add_clinical_rules(self, matcher):
        """Add additional clinical concept matching rules"""
        clinical_concepts = [
            TargetRule("follow up", "FOLLOWUP"),
            TargetRule("recommend", "RECOMMENDATION"),
            TargetRule("suspicious", "SUSPICION"),
            TargetRule("mass", "LESION"),
            TargetRule("lesion", "LESION"),
            TargetRule("nodule", "LESION")
        ]
        matcher.add(clinical_concepts)
        
    def _extract_measurements(self, text: str) -> Dict[str, List[Dict[str, str]]]:
        lines = text.splitlines()
        blocks = []
        for i in range(len(lines) - 3):
            block = ' '.join(lines[i:i+4])
            blocks.append(block)
            # Default fallback units
        default_units = {
        # Vitals
        "Blood Pressure": "mmHg",
        "Heart Rate": "bpm",
        "Respiratory Rate": "breaths/min",
        "Temperature": "°C",
        "SpO2": "%",
        "Height": "cm",
        "Weight": "kg",
        "BMI": "kg/m²",

        # Diabetes
        "Glucose": "mg/dL",
        "HbA1c": "%",

        # Hematology
        "Hemoglobin": "g/dL",
        "Total Leukocyte Count": "cells/cumm",
        "Total RBC Count": "million/cumm",
        "Platelet Count": "lakh/cumm",
        "Hematocrit (HCT)": "%",
        "MCV": "fL",
        "MCH": "pg",
        "MCHC": "g/dL",
        "Neutrophils": "%",
        "Lymphocytes": "%",
        "Monocytes": "%",
        "Eosinophils": "%",
        "Basophils": "%",

        # Lipid Profile
        "Total Cholesterol": "mg/dL",
        "HDL Cholesterol": "mg/dL",
        "LDL Cholesterol": "mg/dL",
        "Triglycerides": "mg/dL",

        # Liver Function
        "SGPT (ALT)": "U/L",
        "SGOT (AST)": "U/L",
        "ALP": "U/L",
        "Bilirubin Total": "mg/dL",
        "Bilirubin Direct": "mg/dL",
        "Albumin": "g/dL",

        # Kidney Function
        "Serum Creatinine": "mg/dL",
        "BUN": "mg/dL",
        "Urea": "mg/dL",
        "eGFR": "mL/min/1.73m²",

        # Electrolytes
        "Sodium": "mmol/L",
        "Potassium": "mmol/L",
        "Calcium": "mg/dL",
        "Phosphate": "mg/dL",
        "Magnesium": "mg/dL",
        "Chloride": "mmol/L",

        # Thyroid
        "TSH": "µIU/mL",
        "T3": "ng/dL",
        "T4": "µg/dL",
        "Insulin": "µIU/mL",

        # Vitamins
        "Vitamin D": "ng/mL",
        "Vitamin B12": "pg/mL",
        "Folate": "ng/mL",
        "Vitamin A": "µg/L",
        "Vitamin E": "mg/L",
        "Vitamin K": "ng/mL",

        # Cardiac Markers
        "Troponin": "ng/mL",
        "CKMB": "U/L",
        "Pro-BNP": "pg/mL",
        "NT-proBNP": "pg/mL",

        # Coagulation
        "INR": "",
        "PT": "sec",
        "PTT": "sec",
        "Fibrinogen": "mg/dL",

        # Inflammation
        "ESR": "mm/hr",
        "CRP": "mg/L",
        "hs-CRP": "mg/L",
        "Procalcitonin": "ng/mL",
        "D-Dimer": "µg/mL",

        # Uric Acid
        "Uric Acid": "mg/dL",

        # Iron Studies
        "Serum Iron": "µg/dL",
        "TIBC": "µg/dL",
        "Transferrin Saturation": "%",

        # Extended Kidney
        "Urine Albumin": "mg/L",
        "Albumin/Creatinine Ratio": "mg/g",

        # Autoimmune
        "Rheumatoid Factor": "IU/mL",
        "Anti-CCP": "U/mL",
        "ANA": "",

        # Tumor Markers
        "PSA": "ng/mL",
        "CA-125": "U/mL",
        "CEA": "ng/mL",
        "AFP": "ng/mL",
        }

        #------all the patterns are written dow
        patterns = {
    # --- Vitals ---
    "Blood Pressure": r"(\d{2,3})/(\d{2,3})\s*mmHg",
    "Heart Rate": r"(\d+)\s*bpm",
    "Respiratory Rate": r"(\d+)\s*breaths/min",
    "Temperature": r"(?i)(?:temperature|temp)\s*[:\-]?\s*(\d{2,3}(?:\.\d+)?)\s*(°?[cCfF])",
    "SpO2": r"(\d+)\s*%\s*SpO2",

    # --- Anthropometric ---
    "Height": r"(?i)height\s*[:\-]?\s*(\d+\.?\d*)\s*(cm|m|ft|in|feet|inches)",
    "Weight": r"(?i)(\d+\.?\d*)\s*(kg|lbs|Ibs)",
    "BMI": r"(?i)BMI\s*[:\-]?\s*(\d+\.?\d*)",

    # --- Blood Glucose / Diabetes ---
    "Glucose": r"(?i)(?:glucose|sugar|bs|rbs|fbs)\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/dl|mg%)?",
    "HbA1c": r"(?i)(?:hba1c|a1c|glycohemoglobin)\s*[:\-]?\s*(\d+\.?\d*)\s*%?",

    # --- Hematology (CBC) ---
    "Hemoglobin": r"(?i)(?:hb|hemoglobin)\s*[:\-]?\s*([\d.,]+)\s*(g/dl|gm%|gram%)?",
    "Total Leukocyte Count": r"(?i)(?:total\s+leukocyte\s+count|tlc|wbc|white\s*blood\s*cells)\s*[:\-]?\s*([\d,]+\.?\d*)\s*(cumm|cells/?cumm|k/μl|k/ul|10\^3/μl)?",
    "Total RBC Count": r"(?i)(?:total\s*rbc\s*count|rbc\s*count|trbc|rbc)\s*[:\-]?\s*([\d,]+\.?\d*)\s*(million/?cumm|10\^6/μl)?",
    "Platelet Count": r"(?i)(?:platelet\s*count|platelets|plt)\s*[:\-]?\s*([\d,]+\.?\d*)\s*(lakhs/?cumm|k/μl|10\^3/μl)?",
    "Hematocrit (HCT)": r"(?i)(?:hematocrit|hct|pcv)\s*[:\-]?\s*([\d.,]+)\s*%?",
    "MCV": r"(?i)MCV\s*[:\-]?\s*([\d.,]+)\s*(fL|fl)?",
    "MCH": r"(?i)MCH\s*[:\-]?\s*([\d.,]+)\s*(pg)?",
    "MCHC": r"(?i)MCHC\s*[:\-]?\s*([\d.,]+)\s*(g/dl|%)?",
    "Neutrophils": r"(?i)neutrophils?\s*[:\-]?\s*([\d.,]+)\s*%?",
    "Lymphocytes": r"(?i)lymphocytes?\s*[:\-]?\s*([\d.,]+)\s*%?",
    "Monocytes": r"(?i)monocytes?\s*[:\-]?\s*([\d.,]+)\s*%?",
    "Eosinophils": r"(?i)eosinophils?\s*[:\-]?\s*([\d.,]+)\s*%?",
    "Basophils": r"(?i)basophils?\s*[:\-]?\s*([\d.,]+)\s*%?",

    # --- Lipid Profile ---
    "Total Cholesterol": r"(?i)total\s*cholesterol\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/dl)?",
    "HDL Cholesterol": r"(?i)hdl\s*cholesterol\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/dl)?",
    "LDL Cholesterol": r"(?i)ldl\s*cholesterol\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/dl)?",
    "Triglycerides": r"(?i)triglycerides\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/dl)?",

    # --- Liver Function ---
    "SGPT (ALT)": r"(?i)(?:sgpt|alt)\s*[:\-]?\s*(\d+\.?\d*)\s*(u/l)?",
    "SGOT (AST)": r"(?i)(?:sgot|ast)\s*[:\-]?\s*(\d+\.?\d*)\s*(u/l)?",
    "ALP": r"(?i)ALP\s*[:\-]?\s*(\d+\.?\d*)\s*(U/L)?",
    "Bilirubin Total": r"(?i)bilirubin\s*total\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/dl)?",
    "Bilirubin Direct": r"(?i)bilirubin\s*direct\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/dl)?",
    "Albumin": r"(?i)albumin\s*[:\-]?\s*(\d+\.?\d*)",

    # --- Kidney Function ---
    "Serum Creatinine": r"(?i)(?:creatinine|scr)\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/dl)?",
    "BUN": r"(?i)BUN\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/dl)?",
    "Urea": r"(?i)urea\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/dl)?",
    "eGFR": r"(?i)eGFR\s*[:\-]?\s*(\d+\.?\d*)",

    # --- Electrolytes ---
    "Sodium": r"(?i)sodium\s*[:\-]?\s*(\d+\.?\d*)",
    "Potassium": r"(?i)potassium\s*[:\-]?\s*(\d+\.?\d*)",
    "Calcium": r"(?i)calcium\s*[:\-]?\s*(\d+\.?\d*)",
    "Phosphate": r"(?i)phosphate\s*[:\-]?\s*(\d+\.?\d*)",
    "Magnesium": r"(?i)magnesium\s*[:\-]?\s*(\d+\.?\d*)",
    "Chloride": r"(?i)chloride\s*[:\-]?\s*(\d+\.?\d*)",

    # --- Thyroid & Hormones ---
    "TSH": r"(?i)TSH\s*[:\-]?\s*(\d+\.?\d*)",
    "T3": r"(?i)T3\s*[:\-]?\s*(\d+\.?\d*)",
    "T4": r"(?i)T4\s*[:\-]?\s*(\d+\.?\d*)",
    "Insulin": r"(?i)insulin\s*[:\-]?\s*(\d+\.?\d*)",

    # --- Vitamins ---
    "Vitamin D": r"(?i)(?:vitamin d|25-oh)\s*[:\-]?\s*(\d+\.?\d*)\s*(ng/ml|nmol/L)?",
    "Vitamin B12": r"(?i)vitamin\s*b12\s*[:\-]?\s*(\d+\.?\d*)",

    # --- Cardiac Markers ---
    "Troponin": r"(?i)troponin\s*[:\-]?\s*(\d+\.?\d*)",
    "CKMB": r"(?i)CK[-\s]?MB\s*[:\-]?\s*(\d+\.?\d*)",
    "Pro-BNP": r"(?i)(?:pro[-\s]?bnp|bnp)\s*[:\-]?\s*(\d+\.?\d*)",

    # --- Coagulation ---
    "INR": r"(?i)INR\s*[:\-]?\s*(\d+\.?\d*)",
    "PT": r"(?i)PT\s*[:\-]?\s*(\d+\.?\d*)",
    "PTT": r"(?i)PTT\s*[:\-]?\s*(\d+\.?\d*)",
    "Fibrinogen": r"(?i)fibrinogen\s*[:\-]?\s*(\d+\.?\d*)",

    # --- Infection / Inflammation ---
    "ESR": r"(?i)ESR\s*[:\-]?\s*(\d+\.?\d*)",
    "CRP": r"(?i)CRP\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/L)?",
    "Procalcitonin": r"(?i)procalcitonin\s*[:\-]?\s*(\d+\.?\d*)",
    "D-Dimer": r"(?i)D-?Dimer\s*[:\-]?\s*(\d+\.?\d*)",

    # --- Uric Acid ---
    "Uric Acid": r"(?i)uric acid\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/dl)?",
    #Iron Studies
    "Serum Iron": r"(?i)serum iron\s*[:\-]?\s*(\d+\.?\d*)\s*(µg/dl|ug/dl)?",
    "TIBC": r"(?i)(?:tibc|total iron binding capacity)\s*[:\-]?\s*(\d+\.?\d*)\s*(µg/dl|ug/dl)?",
    "Transferrin Saturation": r"(?i)transferrin\s*saturation\s*[:\-]?\s*(\d+\.?\d*)\s*%?",
    #Kidney Extended
    "Urine Albumin": r"(?i)(?:urine\s*albumin|microalbuminuria)\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/L|mg/g)?",
    "Albumin/Creatinine Ratio": r"(?i)(?:acr|albumin.creatinine ratio)\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/g)?",
    "hs-CRP": r"(?i)(?:hs.?crp|high.sensitivity crp)\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/L)?",
    "NT-proBNP": r"(?i)(?:nt.?probnp|nt pro bnp)\s*[:\-]?\s*(\d+\.?\d*)",
    "Homocysteine": r"(?i)homocysteine\s*[:\-]?\s*(\d+\.?\d*)\s*(µmol/L|umol/L)?",
    "PSA": r"(?i)(?:psa|prostate specific antigen)\s*[:\-]?\s*(\d+\.?\d*)\s*(ng/ml)?",
    "CA-125": r"(?i)CA.?125\s*[:\-]?\s*(\d+\.?\d*)\s*(U/ml)?",
    "CEA": r"(?i)CEA\s*[:\-]?\s*(\d+\.?\d*)\s*(ng/ml)?",
    "AFP": r"(?i)(?:AFP|alpha fetoprotein)\s*[:\-]?\s*(\d+\.?\d*)\s*(ng/ml)?",
    "HIV": r"(?i)(?:hiv\s*1/?2|anti.?hiv)\s*[:\-]?\s*(reactive|non.?reactive|positive|negative)",
    "HBsAg": r"(?i)(?:hbsag|hepatitis\s*b\s*surface\s*antigen)\s*[:\-]?\s*(reactive|non.?reactive|positive|negative)",
    "HCV": r"(?i)(?:hcv|anti.?hcv)\s*[:\-]?\s*(reactive|non.?reactive|positive|negative)",
    "ANA": r"(?i)(?:ana|antinuclear antibody)\s*[:\-]?\s*(positive|negative|[\d\.]+)",
    "Rheumatoid Factor": r"(?i)(?:rf|rheumatoid\s*factor)\s*[:\-]?\s*(\d+\.?\d*)\s*(IU/ml)?",
    "Anti-CCP": r"(?i)(?:anti.?ccp)\s*[:\-]?\s*(\d+\.?\d*)\s*(U/ml)?",
    "Folate": r"(?i)folate\s*[:\-]?\s*(\d+\.?\d*)\s*(ng/ml)?",
    "Vitamin A": r"(?i)vitamin\s*A\s*[:\-]?\s*(\d+\.?\d*)\s*(µg/L|ug/L)?",
    "Vitamin E": r"(?i)vitamin\s*E\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/L)?",
    "Vitamin K": r"(?i)vitamin\s*K\s*[:\-]?\s*(\d+\.?\d*)\s*(ng/ml)?",
}

        results = defaultdict(list)
        for name, pattern in patterns.items():
            try:
                for m in re.finditer(pattern, text, re.IGNORECASE):
                    raw_val = m.group(1)
                    unit = m.group(2) if len(m.groups()) >= 2 and m.group(2) else ""
                    # fallback to default units
                    if not unit and name in default_units:
                        unit = default_units[name]
                    # commas hatao
                    cleaned = raw_val.replace(",", "").strip()
                    try:
                        num = float(cleaned)
                    except Exception:
                        num = float(re.sub(r"[^\d.]", "", cleaned)) if re.search(r"\d", cleaned) else None
                    if num is not None:
                        results[name].append({"value": num, "unit": unit.strip()})
            except Exception as e:
                print(f"[ERROR] Pattern '{name}': {e}")
        return dict(results)

    
    
    def _predict_specialization(self, doc) -> str:
        """Predict medical specialty with enhanced logic"""
        specialization_map = {
        # Oncology/Radiology
        "breast": "Oncologist",
        "bi-rads": "Radiologist",
        "mammogram": "Radiologist",
        "lesion": "Radiologist",
        "mass": "Radiologist",
        "cancer": "Oncologist",
        
        # Cardiology
        "hypertension": "Cardiologist",
        "blood pressure": "Cardiologist",
        "heart": "Cardiologist",
        "cardiac": "Cardiologist",
        
        # Endocrinology
        "diabetes": "Endocrinologist",
        "hba1c": "Endocrinologist",
        "glucose": "Endocrinologist",
        "thyroid": "Endocrinologist",
        
        # Pulmonology
        "asthma": "Pulmonologist",
        "copd": "Pulmonologist",
        "pneumonia": "Pulmonologist",
        "respiratory": "Pulmonologist",
        
        # Neurology
        "stroke": "Neurologist",
        "epilepsy": "Neurologist",
        "parkinson": "Neurologist",
        "migraine": "Neurologist",
        
        # Gastroenterology
        "hepatitis": "Gastroenterologist",
        "ibd": "Gastroenterologist",
        "crohn": "Gastroenterologist",
        "colon": "Gastroenterologist",
        
        # Rheumatology
        "arthritis": "Rheumatologist",
        "lupus": "Rheumatologist",
        "fibromyalgia": "Rheumatologist",
        
        # Psychiatry
        "depression": "Psychiatrist",
        "anxiety": "Psychiatrist",
        "ptsd": "Psychiatrist",
        "breast": "Oncologist",
        "BI-RADS": "Radiologist",
        "mammogram": "Radiologist",
        "hypertension": "Cardiologist",
        "heart": "Cardiologist",
        "stroke": "Neurologist",
        "parkinson": "Neurologist",
        "diabetes": "Endocrinologist",
        "asthma": "Pulmonologist",
        "cancer": "Oncologist",
        "depression": "Psychiatrist",
        "arthritis": "Rheumatologist",
        "anemia": "Hematologist",
        "epilepsy": "Neurologist",
        "hepatitis": "Gastroenterologist",
        "eczema": "Dermatologist",
        "migraine": "Neurologist",
        "obesity": "Endocrinologist",
        "hemochromatosis": "Hematologist",
        "crohn's disease": "Gastroenterologist",
        "ulcerative colitis": "Gastroenterologist",
        "psoriasis": "Dermatologist",
        "multiple sclerosis": "Neurologist",
        "sickle cell anemia": "Hematologist",
        "autoimmune disease": "Immunologist",
        "chronic kidney disease": "Nephrologist",
        "glaucoma": "Ophthalmologist",
        "macular degeneration": "Ophthalmologist",
        "tuberculosis": "Pulmonologist",
        "dementia": "Neurologist",
        "dengue": "Infectious Disease Specialist",
        "HIV": "Infectious Disease Specialist",
        "lupus": "Rheumatologist",
        "hearing loss": "Otolaryngologist",
        "pneumonia": "Pulmonologist",
        "cystic fibrosis": "Pulmonologist",
        "liver disease": "Gastroenterologist",
        "fibromyalgia": "Rheumatologist",
        "chronic pain": "Pain Specialist",
        "rheumatic fever": "Cardiologist",
        "sepsis": "Infectious Disease Specialist",
        "gout": "Rheumatologist",
        "bipolar disorder": "Psychiatrist",
        "schizophrenia": "Psychiatrist",
        "autism": "Pediatrician",
        "osteoporosis": "Endocrinologist",
        "thyroid disease": "Endocrinologist",
        "anxiety": "Psychiatrist",
        "post-traumatic stress disorder": "Psychiatrist",
        "obstructive sleep apnea": "Pulmonologist",
        "scleroderma": "Rheumatologist",
        "lyme disease": "Infectious Disease Specialist",
        "chronic fatigue syndrome": "Rheumatologist", 
        # Cardiovascular
        "hypertension": "Cardiologist",
        "heart attack": "Cardiologist",
        "heart failure": "Cardiologist",
        "arrhythmia": "Cardiologist",
        "coronary artery disease": "Cardiologist",
        "palpitations": "Cardiologist",
        "chest pain": "Cardiologist",
        
        # Neurological
        "stroke": "Neurologist",
        "parkinson’s disease": "Neurologist",
        "alzheimer’s disease": "Neurologist",
        "epilepsy": "Neurologist",
        "migraine": "Neurologist",
        "multiple sclerosis": "Neurologist",
        "dementia": "Neurologist",
        
        # Endocrine/Metabolic
        "diabetes": "Endocrinologist",
        "hypothyroidism": "Endocrinologist",
        "hyperthyroidism": "Endocrinologist",
        "obesity": "Endocrinologist",
        "pcos": "Endocrinologist",
        "osteoporosis": "Endocrinologist",
        
        # Respiratory
        "asthma": "Pulmonologist",
        "copd": "Pulmonologist",
        "pneumonia": "Pulmonologist",
        "tuberculosis": "Pulmonologist",
        "sleep apnea": "Pulmonologist",
        "chronic cough": "Pulmonologist",
        
        # Gastrointestinal
        "hepatitis": "Gastroenterologist",
        "crohn’s disease": "Gastroenterologist",
        "ulcerative colitis": "Gastroenterologist",
        "gerd": "Gastroenterologist",
        "peptic ulcer": "Gastroenterologist",
        "ibs": "Gastroenterologist",
        "liver cirrhosis": "Gastroenterologist",
        
        # Rheumatology
        "rheumatoid arthritis": "Rheumatologist",
        "osteoarthritis": "Rheumatologist",
        "lupus": "Rheumatologist",
        "fibromyalgia": "Rheumatologist",
        "gout": "Rheumatologist",
        
        # Hematology
        "anemia": "Hematologist",
        "sickle cell anemia": "Hematologist",
        "leukemia": "Hematologist",
        
        # Infectious Diseases
        "dengue": "Infectious Disease Specialist",
        "hiv": "Infectious Disease Specialist",
        "malaria": "Infectious Disease Specialist",
        "covid-19": "Infectious Disease Specialist",
        "sepsis": "Infectious Disease Specialist",
        
        # Oncology
        "breast cancer": "Oncologist",
        "lung cancer": "Oncologist",
        "prostate cancer": "Oncologist",
        "colon cancer": "Oncologist",
        "leukemia": "Oncologist",
        
        # Psychiatry
        "depression": "Psychiatrist",
        "anxiety": "Psychiatrist",
        "bipolar disorder": "Psychiatrist",
        "schizophrenia": "Psychiatrist",
        "ptsd": "Psychiatrist",
        "adhd": "Psychiatrist",
        
        # Dermatology
        "eczema": "Dermatologist",
        "psoriasis": "Dermatologist",
        "acne": "Dermatologist",
        "skin rash": "Dermatologist",
        
        # Nephrology
        "chronic kidney disease": "Nephrologist",
        "kidney stones": "Nephrologist",
        
        # Urology
        "uti": "Urologist",
        "prostate enlargement": "Urologist",
        "erectile dysfunction": "Urologist",
        
        # Gynecology
        "pcos": "Gynecologist",
        "endometriosis": "Gynecologist",
        "menopause": "Gynecologist",
        "ovarian cysts": "Gynecologist",
        
        # ENT
        "sinusitis": "ENT Specialist",
        "hearing loss": "ENT Specialist",
        "tonsillitis": "ENT Specialist",
        
        # Ophthalmology
        "glaucoma": "Ophthalmologist",
        "cataract": "Ophthalmologist",
        
        # General Practice (catch-all)
        "fever": "General Physician",
        "cold": "General Physician",
        "flu": "General Physician",
        "headache": "General Physician",
        "fatigue": "General Physician"

    }

        text = doc.text.lower()
        for keywords, spec in specialization_map.items():
            if re.search(keywords, text):
                return spec
                
        return "General Physician"
    
    
    def process_text(self, text):
        measurement = self._extract_measurements(text)
        doc = self.nlp(text)
        diseases = self._extract_diseases(doc)
        specialization = self._predict_specialization(doc)
        return {
            "measurements": measurements,
            "diseases": diseases,
            "specialization": specialization
        }

    def _extract_diseases(self, doc) -> List[str]:
        """Extract disease entities from the processed doc"""
        diseases = []
        for ent in doc.ents:
            if ent.label_ == "DISEASE":
                diseases.append(self._normalize_disease(ent.text))
        return sorted(set(diseases))


    def _extract_key_findings(self, text: str) -> str:
        """Extract impression/findings section with improved regex"""
        findings_match = re.search(
            r"(IMPRESSION|FINDINGS|CONCLUSION|OPINION)[:\s]*(.*?)(?=\n\n|\Z)", 
            text, re.IGNORECASE | re.DOTALL)
        return findings_match.group(2).strip() if findings_match else ""

    def _extract_recommendations(self, doc) -> List[str]:
        """Extract clinical recommendations from text"""
        recommendations = []
        for sent in doc.sents:
            if any(token.text.lower() in {"recommend", "suggest", "advise"} for token in sent):
                recommendations.append(sent.text)
        return recommendations
    
    def fuzzy_match_diseases(self, text: str, threshold: int = 85) -> List[str]:
        """Fallback fuzzy matching for unrecognized disease terms"""
        found = set()
        words = set(re.findall(r"\b[\w-]+\b", text.lower()))
        
        for word in words:
            if len(word) < 4:  # Skip short words
                continue
                
            match, score = process.extractOne(word, self.diseases)
            if score >= threshold:
                found.add(match)
                
        return sorted(found)
    def process_text(self, text):
        print(f"\n=== NLP INPUT ===\n{text}\n")

        doc = self.nlp(text)
        diseases = self._extract_diseases(doc)
        measurements = self._extract_measurements(text)
        findings = self._extract_key_findings(text)
        recommendations = self._extract_recommendations(doc)
        specialization = self._predict_specialization(doc)

        analysis = {
            "measurements": measurements,
            "diseases": diseases,
            "specialization": specialization,
            "findings": findings,
            "recommendations": recommendations
        }

        # Debug print the full analysis
        print("\n=== NLP ANALYSIS ===")
        print(json.dumps(analysis, indent=2))  # Pretty-print as JSON
        print("===================\n")

        return analysis
