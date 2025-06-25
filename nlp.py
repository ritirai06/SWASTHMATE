import re
import spacy
from spacy.tokens import Span
from fuzzywuzzy import process
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

    def process_text(self, text):
        print(f"DEBUG: Input text (first 200 chars): {text[:200]}")  # Debug 3
        
        doc = self.nlp(text)
        
        print(f"DEBUG: Found {len(doc.ents)} entities")  # Debug 4
         
         
        # Extract diseases and deduplicate
        diseases = self._extract_diseases(doc)
        
        unique_diseases = {}
        for d in diseases:
            key = (d['text'].lower(), d['section'])
            if key not in unique_diseases:
                unique_diseases[key] = d
        diseases = list(unique_diseases.values())
        
        return {
            "measurements": self._extract_measurements(text),
            "diseases": self._extract_diseases(doc),
            "specialization": self._predict_specialization(doc),
            "findings": self._extract_key_findings(text),
            "recommendations": self._extract_recommendations(doc)
        }
    def _extract_measurements(self, text: str) -> Dict[str, List[Dict[str, str]]]:
        """Enhanced measurement extraction with breast imaging focus"""
        patterns = {
        # Breast Imaging Specific
         "Lesion Size": r"(\d+\.?\d*)\s*[x×]\s*(\d+\.?\d*)\s*cm",
        "BI-RADS Category": r"BI-RADS\s*[-]?\s*([0-6IV]+)",
        "Clock Position": r"(\d+)\s*(?:o['′]?clock|oclock)",
         "Mass Margin": r"(circumscribed|microlobulated|obscured|indistinct|spiculated)\s*margin",
            
         # Vitals and Lab Measurements (condensed)
        "Blood Pressure": r"(\d{2,3})/(\d{2,3})\s*mmHg",
        "Glucose": r"(?i)(?:glucose|sugar)[\s:]*(\d+)\s*(?:mg/dl|mg%)",
        "Hemoglobin": r"(?i)(?:hb|hemoglobin)[\s:]*(\d+\.?\d*)\s*(?:g/dl)",
        # Vitals
        "Height": r"(?i)(?:height)[\s:]*(\d+\.?\d*)\s*(cm|m|ft|in|feet|inches)",
        "BMI": r"BMI\s*[:\-]?\s*(\d+\.?\d*)",
        "Weight": r"(\d+\.?\d*)\s*(kg|lbs|Ibs)",
        "Blood Pressure": r"(\d{2,3})/(\d{2,3})\s*mmHg",
        "Heart Rate": r"(\d+)\s*bpm",
        "Temperature": r"(temperature|temp)\s*[:\-]?\s*(\d{2,3}(?:\.\d+)?)\s*(°?[cCfF])?",  
        "Respiratory Rate": r"(\d+)\s*breaths/min",
        "SpO2": r"(\d+)%\s*SpO2",
        "Fever": r"(?i)(?:fever|temp|temperature)[\s:]*(\d{2,3}\.?\d*)\s*°?[CF]",

        # Blood tests
        "Hemoglobin": r"(?i)(?:hb|hemoglobin)[\s:]*(\d+\.?\d*)\s*(?:g/dl|g/dL|gm%|gram%)",
        "WBC Count": r"(?i)(?:wbc|white blood cells)[\s:]*(\d+\.?\d*)\s*(?:K/μL|k/ul|x10³/μL)",
        "Platelets": r"(?i)(?:platelets|plt)[\s:]*(\d+)\s*(?:K/μL|x10³/μL)",
        "Glucose": r"(?i)(?:glucose|sugar|bs|rbs|fbs)[\s:]*(\d+)\s*(?:mg/dl|mg%)",
        "HbA1c": r"(?i)(?:hba1c|a1c|glycohemoglobin)[\s:]*(\d+\.?\d*)\s*%",
        "Serum Creatinine": r"(?i)(?:creatinine|scr)[\s:]*(\d+\.?\d*)\s*(?:mg/dl)",
        "BUN": r"(?i)(?:bun|urea nitrogen)[\s:]*(\d+)\s*(?:mg/dl)",
        "RBC": r"RBC\s*[:\-]?\s*(\d+\.?\d*)",
        "Platelets": r"Platelets\s*[:\-]?\s*(\d+\.?\d*)",
        "ESR": r"ESR\s*[:\-]?\s*(\d+\.?\d*)",
        "CRP": r"CRP\s*[:\-]?\s*(\d+\.?\d*)\s*mg/L",
        "LDH": r"LDH\s*[:\-]?\s*(\d+\.?\d*)",
        "PT": r"PT\s*[:\-]?\s*(\d+\.?\d*)",
        "PTT": r"PTT\s*[:\-]?\s*(\d+\.?\d*)",
        "INR": r"INR\s*[:\-]?\s*(\d+\.?\d*)",
        "D-Dimer": r"D-Dimer\s*[:\-]?\s*(\d+\.?\d*)",
        "Fibrinogen": r"Fibrinogen\s*[:\-]?\s*(\d+\.?\d*)",
        
        # Lipid profile
        "Cholesterol": r"Total Cholesterol\s*[:\-]?\s*(\d+\.?\d*)",
        "HDL": r"HDL\s*[:\-]?\s*(\d+\.?\d*)",
        "LDL": r"LDL\s*[:\-]?\s*(\d+\.?\d*)",
        "Triglycerides": r"Triglycerides\s*[:\-]?\s*(\d+\.?\d*)",
        # Liver
        "ALT": r"ALT\s*[:\-]?\s*(\d+\.?\d*)",
        "AST": r"AST\s*[:\-]?\s*(\d+\.?\d*)",
        "ALP": r"ALP\s*[:\-]?\s*(\d+\.?\d*)",
        "Bilirubin": r"Bilirubin\s*[:\-]?\s*(\d+\.?\d*)",
        "Albumin": r"Albumin\s*[:\-]?\s*(\d+\.?\d*)",
        # Kidney
        "Creatinine": r"Creatinine\s*[:\-]?\s*(\d+\.?\d*)",
        "Urea": r"Urea\s*[:\-]?\s*(\d+\.?\d*)",
        "BUN": r"BUN\s*[:\-]?\s*(\d+\.?\d*)",
        "eGFR": r"eGFR\s*[:\-]?\s*(\d+\.?\d*)",
        # Electrolytes
        "Sodium": r"Sodium\s*[:\-]?\s*(\d+\.?\d*)",
        "Potassium": r"Potassium\s*[:\-]?\s*(\d+\.?\d*)",
        "Calcium": r"Calcium\s*[:\-]?\s*(\d+\.?\d*)",
        "Magnesium": r"Magnesium\s*[:\-]?\s*(\d+\.?\d*)",
        "Chloride": r"Chloride\s*[:\-]?\s*(\d+\.?\d*)",
        # Additional measurements
        "TSH": r"TSH\s*[:\-]?\s*(\d+\.?\d*)",
        "T3": r"T3\s*[:\-]?\s*(\d+\.?\d*)",
        "T4": r"T4\s*[:\-]?\s*(\d+\.?\d*)",
        "Uric Acid": r"Uric Acid\s*[:\-]?\s*(\d+\.?\d*)",
        "Ferritin": r"Ferritin\s*[:\-]?\s*(\d+\.?\d*)",
        "Vitamin B12": r"Vitamin B12\s*[:\-]?\s*(\d+\.?\d*)",
        "D-Dimer": r"D-Dimer\s*[:\-]?\s*(\d+\.?\d*)",
        "Troponin": r"Troponin\s*[:\-]?\s*(\d+\.?\d*)",
        "PSA": r"PSA\s*[:\-]?\s*(\d+\.?\d*)",
        # Chronic Conditions with Severity
        "Hypertension Stage": r"(?i)(?:hypertension|htn)[\s:]*(stage [12]|\d{2,3}/\d{2,3})",
        "Diabetes Control": r"(?i)(?:diabetes|dm)[\s:]*(poorly|well)[-]?controlled",
        "Asthma Severity": r"(?i)(?:asthma)[\s:]*(mild|moderate|severe|intermittent|persistent)",
        # Quantitative Symptoms
        "Weight Loss": r"(?i)(?:weight loss|lost)[\s:]*(\d+)\s*(kg|lbs|pounds?)(?:\s*in\s*(\d+)\s*(?:months?|weeks?|days?))?",
        "Pain Score": r"(?i)(?:pain)[\s:]*(\d)\s*[-]?\s*(\d)\s*(?:/10|out of 10)",
        "Bleeding Duration": r"(?i)(?:bleeding|menstrual|period)[\s:]*last(?:ing|ed)?\s*(\d+)\s*(?:days|hours)",
    
        # Infection Markers
        "COVID-19 Test": r"(?i)(?:covid|sars-cov-2)[\s:]*((?:pcr|rapid|antigen)?\s*(?:positive|negative|\+|\-))",
        "Infection Count": r"(?i)(?:wbc|white cells)[\s:]*elevated\s*at\s*(\d+)\s*(?:K/μL)",
    
        # Specialized Tests
        "PSA Level": r"(?i)(?:psa)[\s:]*(\d+\.?\d*)\s*(?:ng/ml)",
        "Vitamin D": r"(?i)(?:vit d|25-oh)[\s:]*(\d+)\s*(?:ng/ml|nmol/L)",
        "Thyroid TSH": r"(?i)(?:tsh|thyroid)[\s:]*(\d+\.?\d*)\s*(?:μIU/ml|mIU/L)",
    
        # Medication Dosages
        "Insulin Dose": r"(?i)(?:insulin)[\s:]*(\d+)\s*(?:units|iu)(?:\s*(?:bid|tid|qid|daily))?",
        "Warfarin Dose": r"(?i)(?:warfarin|coumadin)[\s:]*(\d+\.?\d*)\s*(?:mg)(?:\s*(?:daily|od))?"
        }
        
        results = defaultdict(list)
        for name, pattern in patterns.items():
            try:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for m in matches:
                 if name == "Blood Pressure":
                    systolic, diastolic = m.group(1), m.group(2)
                    unit = m.group(3) if m.group(3) else "mmHg"
                    results[name].append({
                        "value": f"{systolic}/{diastolic}",
                        "unit": unit
                    })
                 elif name == "Lesion Size":
                    results[name].append({
                        "value": m.group(1),
                        "unit": "cm"
                    })
                 elif name == "Clock Position":
                    results[name].append({
                        "value": f"{m.group(1)} o'clock"
                    })
                 elif len(m.groups()) >= 2:
                  value, unit = m.group(1), m.group(2)
                  results[name].append({
                           "value": float(value) if '.' in value else int(value),
                        "unit": unit
                    })
                 else:
                    results[name].append({
                        "value": m.group(1)
                    })
            except Exception as e:
             print(f"Error processing pattern {name}: {e}")
    
        return dict(results)

    def _extract_diseases(self, doc) -> List[Dict]:
        """Extract diseases with clinical context"""
        diseases = []
        for ent in doc.ents:
            if ent.label_ == "DISEASE":
                normalized_text = self._normalize_disease(ent.text)
                diseases.append({
                    "text": normalized_text,
                    "negated": ent._.is_negated,
                    "uncertain": ent._.is_uncertain,
                    "historical": ent._.is_historical,
                    "section": str(ent._.section_title).rstrip(':') if hasattr(ent._, "section_title")and ent._.section_title else None
                })
        return diseases

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


# Singleton instance for application use
nlp_processor = MedicalNLP()


# Example usage
if __name__ == "__main__":
    sample_report = """
    Patient presents with fatigue and chest pain. 
    HISTORY: Hypertension, diabetes (poorly controlled).
    FINDINGS: 
    - Blood Pressure: 150/95 mmHg
    - Glucose: 210 mg/dL
    - Mammogram shows 1.5x2.0 cm mass at 3 o'clock (BI-RADS 4)
    IMPRESSION: 
    1. Suspicious breast lesion, recommend biopsy
    2. Uncontrolled diabetes
    """
    
    results = nlp_processor.process_text(sample_report)
    
    from pprint import pprint
    print("\nMedical Report Analysis Results:")
    pprint(results)