# medical_nlp.py - Medical Natural Language Processing module
import json
import re
import spacy
from spacy.tokens import Span
from rapidfuzz import process, fuzz
from medspacy.ner import TargetRule
from typing import Dict, List, Set
from collections import defaultdict
import concurrent.futures
import threading

class MedicalNLP:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern for faster initialization"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MedicalNLP, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the medical NLP processor with models and rules"""
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        
        # Optimize spaCy loading - disable unnecessary pipes for speed
        self.nlp = spacy.load("en_core_web_sm", disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer"])
        print("DEBUG: SpaCy model loaded successfully (optimized)")
        
        # Load vocabularies
        self.diseases = self._load_disease_vocabulary()
        self.medicines = self._load_medicine_vocabulary()
        print(f"DEBUG: Loaded {len(self.diseases)} diseases and {len(self.medicines)} medicines")
        
        # Setup pipelines
        self._setup_pipelines()
        
        # Compile regex patterns for faster matching
        self._compile_patterns()
        
        # Cache for fuzzy matching
        self._disease_cache = {}
        self._medicine_cache = {}
        
    def _setup_pipelines(self):
        """Setup optimized NLP pipelines"""
        # Only add essential pipes for medical text
        if "sentencizer" not in self.nlp.pipe_names:
            self.nlp.add_pipe("sentencizer")
        
        # Try to add medspacy components if available
        try:
            if "medspacy_target_matcher" not in self.nlp.pipe_names:
                self.nlp.add_pipe("medspacy_target_matcher")
            if "medspacy_context" not in self.nlp.pipe_names:
                self.nlp.add_pipe("medspacy_context")
        except Exception as e:
            print(f"Note: MedSpaCy components not available: {e}")
    
    def _load_medicine_vocabulary(self) -> Set[str]:
        """Load comprehensive medicine vocabulary from text_analyzer"""
        try:
            from text_analyzer import MEDICATION_CANON
            # Extract all medicine names from MEDICATION_CANON
            medicines = set(MEDICATION_CANON.keys())
            # Also add common brand names
            medicines.update({
                "Paracetamol", "Ibuprofen", "Aspirin", "Metformin", "Amlodipine",
                "Atorvastatin", "Pantoprazole", "Omeprazole", "Azithromycin",
                "Amoxicillin", "Cefixime", "Levipil", "Taxol", "Insulin",
                "Levothyroxine", "Prednisolone", "Dexamethasone", "Warfarin",
                "Clopidogrel", "Ecosprin", "Losartan", "Telmisartan", "Ramipril",
                "Salbutamol", "Montelukast", "Cetirizine", "Furosemide",
                "Dolo", "Crocin", "Glycomet", "Pantazol", "Azit", "Amlo"
            })
            return medicines
        except ImportError:
            # Fallback if text_analyzer not available
            return {
                "Paracetamol", "Ibuprofen", "Aspirin", "Metformin", "Amlodipine",
                "Atorvastatin", "Pantoprazole", "Omeprazole", "Azithromycin",
                "Amoxicillin", "Cefixime", "Levipil", "Taxol", "Insulin"
            }
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for faster matching - expanded patterns"""
        # Disease patterns - expanded
        self.disease_patterns = [
            re.compile(r'\b(diabetes|diabetes mellitus|dm|type 1 diabetes|type 2 diabetes)\b', re.I),
            re.compile(r'\b(hypertension|htn|high blood pressure|bp)\b', re.I),
            re.compile(r'\b(pneumonia|bronchitis|bronchiolitis|pneumonitis)\b', re.I),
            re.compile(r'\b(asthma|copd|chronic obstructive pulmonary disease)\b', re.I),
            re.compile(r'\b(tuberculosis|tb|pulmonary tb)\b', re.I),
            re.compile(r'\b(covid-19|covid|coronavirus|sars-cov-2)\b', re.I),
            re.compile(r'\b(cancer|carcinoma|tumor|malignancy|neoplasm|oncology)\b', re.I),
            re.compile(r'\b(heart attack|myocardial infarction|mi|cardiac arrest)\b', re.I),
            re.compile(r'\b(stroke|cva|cerebrovascular accident|brain attack)\b', re.I),
            re.compile(r'\b(epilepsy|seizure|convulsion|fits)\b', re.I),
            re.compile(r'\b(parkinson|alzheimer|dementia|memory loss)\b', re.I),
            re.compile(r'\b(arthritis|rheumatoid|osteoarthritis|ra|oa)\b', re.I),
            re.compile(r'\b(kidney disease|ckd|chronic kidney disease|renal failure)\b', re.I),
            re.compile(r'\b(liver disease|hepatitis|cirrhosis|fatty liver)\b', re.I),
            re.compile(r'\b(thyroid|hypothyroidism|hyperthyroidism|goiter)\b', re.I),
            re.compile(r'\b(anemia|iron deficiency|vitamin deficiency)\b', re.I),
            re.compile(r'\b(depression|anxiety|ptsd|bipolar|schizophrenia)\b', re.I),
            re.compile(r'\b(uti|urinary tract infection|cystitis)\b', re.I),
            re.compile(r'\b(gastritis|gerd|peptic ulcer|ibd|ibs)\b', re.I),
            re.compile(r'\b(migraine|headache|cluster headache)\b', re.I),
        ]
        
        # Medicine patterns - expanded with more medicines
        self.medicine_patterns = [
            re.compile(r'\b(paracetamol|acetaminophen|dolo|crocin|tylenol)\b', re.I),
            re.compile(r'\b(metformin|glucophage|glycomet|metfor)\b', re.I),
            re.compile(r'\b(amlodipine|amlodep|amlo|norvasc)\b', re.I),
            re.compile(r'\b(atorvastatin|atorva|lipitor|ator)\b', re.I),
            re.compile(r'\b(pantoprazole|pantazol|pantaprazole|pantodac)\b', re.I),
            re.compile(r'\b(azithromycin|azit|azithral|zithromax)\b', re.I),
            re.compile(r'\b(amoxicillin|amoxycilin|amoxil|augmentin)\b', re.I),
            re.compile(r'\b(levipil|levetiracetam|levepil|keppra)\b', re.I),
            re.compile(r'\b(insulin|humalog|lantus|novolog|humulin)\b', re.I),
            re.compile(r'\b(aspirin|ecosprin|disprin|asa)\b', re.I),
            re.compile(r'\b(ibuprofen|brufen|advil|motrin)\b', re.I),
            re.compile(r'\b(omeprazole|omez|prilosec|omep)\b', re.I),
            re.compile(r'\b(losartan|cozaar|losar)\b', re.I),
            re.compile(r'\b(ramipril|altace|ramip)\b', re.I),
            re.compile(r'\b(telmisartan|micardis|telma)\b', re.I),
            re.compile(r'\b(levothyroxine|eltroxin|thyronorm|synthroid)\b', re.I),
            re.compile(r'\b(prednisolone|prednisone|deltasone)\b', re.I),
            re.compile(r'\b(dexamethasone|decadron|dexona)\b', re.I),
            re.compile(r'\b(warfarin|coumadin|warf)\b', re.I),
            re.compile(r'\b(clopidogrel|plavix|clopid)\b', re.I),
            re.compile(r'\b(salbutamol|ventolin|albuterol)\b', re.I),
            re.compile(r'\b(montelukast|singulair|montair)\b', re.I),
            re.compile(r'\b(cetirizine|zyrtec|cetrizin)\b', re.I),
            re.compile(r'\b(furosemide|lasix|frusemide)\b', re.I),
            re.compile(r'\b(cefixime|cefix|suprax)\b', re.I),
            re.compile(r'\b(ceftriaxone|rocephin|ceftriax)\b', re.I),
            re.compile(r'\b(doxycycline|doxy|vibramycin)\b', re.I),
            re.compile(r'\b(fluconazole|diflucan|flucan)\b', re.I),
            re.compile(r'\b(acyclovir|zovirax|acyclo)\b', re.I),
            re.compile(r'\b(sertraline|zoloft|sertra)\b', re.I),
            re.compile(r'\b(fluoxetine|prozac|fluox)\b', re.I),
            re.compile(r'\b(sildenafil|viagra|silden)\b', re.I),
            re.compile(r'\b(tadalafil|cialis|tadala)\b', re.I),
        ]
        
        # Recommendation patterns - expanded with more keywords
        self.recommendation_patterns = [
            re.compile(r'(?:recommend|recommendation|suggest|suggestion|advise|advice|prescribe|prescription)\s+([^\.]+)', re.I),
            re.compile(r'(?:should|must|need to|required to|advised to)\s+([^\.]+)', re.I),
            re.compile(r'(?:follow|continue|maintain|keep|take|use|apply)\s+([^\.]+)', re.I),
            re.compile(r'(?:follow.?up|re.?visit|return|next appointment|schedule|book)\s+([^\.]+)', re.I),
            re.compile(r'(?:avoid|do not|don\'t|refrain from|stop|discontinue|cease)\s+([^\.]+)', re.I),
            re.compile(r'(?:monitor|check|test|measure|track|watch)\s+([^\.]+)', re.I),
            re.compile(r'(?:increase|decrease|reduce|limit|restrict|modify)\s+([^\.]+)', re.I),
            re.compile(r'(?:exercise|physical activity|workout|fitness|yoga|walking)\s+([^\.]+)', re.I),
            re.compile(r'(?:diet|nutrition|food|meal|eat|consume|intake)\s+([^\.]+)', re.I),
            re.compile(r'(?:rest|sleep|hydration|water|fluids|drink)\s+([^\.]+)', re.I),
            re.compile(r'(?:consult|see|visit|meet|contact|call|refer)\s+([^\.]+)', re.I),
            re.compile(r'(?:emergency|urgent|immediate|asap|right away)\s+([^\.]+)', re.I),
            re.compile(r'(?:prevent|prevention|protect|protection)\s+([^\.]+)', re.I),
            re.compile(r'(?:treatment|therapy|medication|medicine|drug)\s+([^\.]+)', re.I),
        ]
    
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
        """Cached disease normalization for faster processing"""
        text_lower = text.lower().strip()
        if not text_lower or len(text_lower) < 3:
            return text_lower
        
        # Check cache first
        if text_lower in self._disease_cache:
            return self._disease_cache[text_lower]
        
        # Try exact match first (fastest)
        diseases_lower = {d.lower(): d for d in self.diseases}
        if text_lower in diseases_lower:
            result = diseases_lower[text_lower]
            self._disease_cache[text_lower] = result
            return result
        
        # Fuzzy match with higher threshold for speed
        result = process.extractOne(text_lower, self.diseases, scorer=fuzz.token_sort_ratio)
        if result and len(result) >= 2:
            match, score = result[0], result[1]
            if score >= 85:
                self._disease_cache[text_lower] = match
                return match
        
        self._disease_cache[text_lower] = text_lower
        return text_lower
    
    def _normalize_medicine(self, text):
        """Cached medicine normalization"""
        text_lower = text.lower().strip()
        if not text_lower:
            return text_lower
        
        if text_lower in self._medicine_cache:
            return self._medicine_cache[text_lower]
        
        medicines_lower = {m.lower(): m for m in self.medicines}
        if text_lower in medicines_lower:
            result = medicines_lower[text_lower]
            self._medicine_cache[text_lower] = result
            return result
        
        result = process.extractOne(text_lower, self.medicines, scorer=fuzz.token_sort_ratio)
        if result and len(result) >= 2:
            match, score = result[0], result[1]
            if score >= 85:
                self._medicine_cache[text_lower] = match
                return match
        
        self._medicine_cache[text_lower] = text_lower
        return text_lower


    def _load_disease_vocabulary(self) -> Set[str]:
        """Load comprehensive disease vocabulary - expanded with more conditions"""
        diseases = {
        # Breast Imaging Specific
        "BI-RADS 0", "BI-RADS 1", "BI-RADS 2", "BI-RADS 3", 
        "BI-RADS 4", "BI-RADS 5", "BI-RADS 6",
        "Ductal Carcinoma", "Lobular Carcinoma", 
        "Fibroadenoma", "Breast Cyst", "Microcalcifications",
        
        # General Symptoms
        "Fever", "Cold", "Flu", "Sore Throat", "Cough", "Body Ache", "Fatigue", "Headache", "Nausea",
        "Vomiting", "Diarrhea", "Constipation", "Abdominal Pain", "Dizziness", "Chest Pain", "Back Pain",
        "Joint Pain", "Muscle Cramps", "Shortness of Breath", "Palpitations", "Loss of Appetite",
        "Weight Loss", "Weight Gain", "Period Pain", "Irregular Periods", "Heavy Menstrual Bleeding",
        "Vaginal Discharge", "Night Sweats", "Skin Rash", "Itching", "Nosebleeds", "Dry Mouth",
        "Sweating Excessively", "Insomnia", "Burning Sensation in Urine", "Frequent Urination",
        "Painful Urination", "Burning Sensation in Eyes", "Blurred Vision", "Eye Pain",
            
        # Infections & Acute Conditions
        "Viral Fever", "Dengue", "Chikungunya", "Malaria", "Typhoid", "COVID-19", "Tuberculosis", "TB",
        "Pneumonia", "Bronchitis", "Sinusitis", "Tonsillitis", "Ear Infection", "Conjunctivitis", 
        "Strep Throat", "UTI", "Vaginal Yeast Infection", "Bacterial Vaginosis", "Skin Infection", 
        "Gastroenteritis", "Hepatitis A", "Hepatitis B", "Hepatitis C", "HIV", "AIDS", "STIs", 
        "STD", "Genital Herpes", "Scabies", "Chickenpox", "Measles", "Mumps", "Ringworm", "Jaundice",
        "Sepsis", "Cellulitis", "Impetigo", "Folliculitis", "Otitis Media", "Pharyngitis", "Laryngitis",
        "Bronchiolitis", "Pneumonitis", "Meningitis", "Encephalitis", "Myocarditis", "Pericarditis",
        "Appendicitis", "Diverticulitis", "Pancreatitis", "Cholecystitis", "Pyelonephritis",
        "Cystitis", "Prostatitis", "Epididymitis", "Orchitis", "Vaginitis", "Cervicitis",
        "Endometritis", "Salpingitis", "Oophoritis", "Pelvic Inflammatory Disease", "PID",

        # Chronic & Systemic Diseases
        "Diabetes", "Type 1 Diabetes", "Type 2 Diabetes", "Diabetes Mellitus", "DM", "Hypertension", 
        "HTN", "High Blood Pressure", "Hypothyroidism", "Hyperthyroidism", "Thyroid Disorder",
        "High Cholesterol", "Hyperlipidemia", "Dyslipidemia", "Obesity", "PCOS", "Polycystic Ovary Syndrome",
        "Endometriosis", "Anemia", "Iron Deficiency Anemia", "Vitamin D Deficiency", "Vitamin B12 Deficiency",
        "Folate Deficiency", "Osteoporosis", "Osteopenia", "Rheumatoid Arthritis", "RA", "Osteoarthritis", "OA",
        "Asthma", "COPD", "Chronic Obstructive Pulmonary Disease", "Chronic Sinusitis", "GERD", 
        "Gastroesophageal Reflux Disease", "Gastritis", "Peptic Ulcer", "Gastric Ulcer", "Duodenal Ulcer",
        "IBS", "Irritable Bowel Syndrome", "IBD", "Inflammatory Bowel Disease", "Crohn's Disease",
        "Ulcerative Colitis", "Celiac Disease", "Fatty Liver Disease", "NAFLD", "NASH",
        "Liver Cirrhosis", "CKD", "Chronic Kidney Disease", "Kidney Stones", "Nephrolithiasis",
        "Gallstones", "Cholelithiasis", "Migraine", "Epilepsy", "Seizure Disorder", "Parkinson's Disease",
        "Alzheimer's Disease", "Dementia", "Multiple Sclerosis", "MS", "Lupus", "SLE", "Systemic Lupus Erythematosus",
        "Fibromyalgia", "Scleroderma", "Psoriasis", "Vitiligo", "Alopecia", "Rosacea", "Acne",
        "Eczema", "Atopic Dermatitis", "Contact Dermatitis", "Seborrheic Dermatitis", "Urticaria", "Hives",

        # Cardiac, Respiratory, Neuro
        "Coronary Artery Disease", "CAD", "Heart Attack", "Myocardial Infarction", "MI", "Stroke", "CVA",
        "Cerebrovascular Accident", "Heart Failure", "CHF", "Congestive Heart Failure", "Arrhythmia",
        "Atrial Fibrillation", "AFib", "Bradycardia", "Tachycardia", "Angina", "Cardiomyopathy",
        "Valvular Heart Disease", "Aortic Stenosis", "Mitral Regurgitation", "Peripheral Artery Disease",
        "PAD", "Deep Vein Thrombosis", "DVT", "Pulmonary Embolism", "PE", "Hypertensive Heart Disease",
        "Anxiety Disorder", "Generalized Anxiety Disorder", "GAD", "Depression", "Major Depressive Disorder",
        "MDD", "Panic Disorder", "PTSD", "Post Traumatic Stress Disorder", "Schizophrenia",
        "Bipolar Disorder", "ADHD", "Attention Deficit Hyperactivity Disorder", "Autism Spectrum Disorder",
        "ASD", "Autism", "Sleep Apnea", "Obstructive Sleep Apnea", "OSA", "Restless Leg Syndrome",
        "Narcolepsy", "Insomnia Disorder", "Dystonia", "Tremor", "Essential Tremor", "Huntington's Disease",
        "ALS", "Amyotrophic Lateral Sclerosis", "Bell's Palsy", "Trigeminal Neuralgia", "Peripheral Neuropathy",
        "Diabetic Neuropathy", "Guillain-Barre Syndrome", "Myasthenia Gravis", "Muscular Dystrophy",

        # Women's Health
        "Menopause", "Perimenopause", "Hormonal Imbalance", "Infertility", "Infertility (Female)",
        "PMS", "Premenstrual Syndrome", "PMDD", "Breast Lumps", "Ovarian Cysts", "Cervical Cancer",
        "Uterine Fibroids", "Endometrial Cancer", "Ovarian Cancer", "Vulvar Cancer", "Vaginal Cancer",
        "Ectopic Pregnancy", "Miscarriage", "Stillbirth", "Preeclampsia", "Eclampsia", "Gestational Diabetes",
        "Placenta Previa", "Placental Abruption", "Ovarian Torsion", "Endometrial Hyperplasia",
        "Adenomyosis", "Pelvic Organ Prolapse", "Urinary Incontinence", "Stress Incontinence",

        # Men's Health
        "Erectile Dysfunction", "ED", "Premature Ejaculation", "PE", "Infertility (Male)", "Male Infertility",
        "Prostate Enlargement", "BPH", "Benign Prostatic Hyperplasia", "Prostate Cancer",
        "Testicular Cancer", "Penile Cancer", "Varicocele", "Hydrocele", "Phimosis", "Priapism",
        "Low Testosterone", "Hypogonadism", "Gynecomastia", "Male Pattern Baldness", "Androgenetic Alopecia",

        # Pediatric & Geriatric
        "Iron Deficiency in Children", "Growth Delay", "Failure to Thrive", "Childhood Obesity",
        "Bedwetting", "Enuresis", "ADHD in Kids", "Autism in Children", "Developmental Delay",
        "Cerebral Palsy", "Down Syndrome", "Cystic Fibrosis", "Sickle Cell Disease", "Thalassemia",
        "Hemophilia", "Kawasaki Disease", "Rheumatic Fever", "Juvenile Arthritis", "Type 1 Diabetes in Children",
        "Aging-Related Memory Loss", "Mild Cognitive Impairment", "Falls in Elderly", "Osteoporosis in Elderly",
        "Elderly Depression", "Elder Abuse", "Polypharmacy", "Frailty", "Sarcopenia",

        # Oncology - Expanded
        "Breast Cancer", "Lung Cancer", "Colon Cancer", "Colorectal Cancer", "Skin Cancer", "Melanoma",
        "Basal Cell Carcinoma", "Squamous Cell Carcinoma", "Leukemia", "Acute Lymphoblastic Leukemia", "ALL",
        "Acute Myeloid Leukemia", "AML", "Chronic Lymphocytic Leukemia", "CLL", "Chronic Myeloid Leukemia", "CML",
        "Pancreatic Cancer", "Brain Tumor", "Glioblastoma", "Meningioma", "Liver Cancer", "Hepatocellular Carcinoma",
        "Stomach Cancer", "Gastric Cancer", "Esophageal Cancer", "Kidney Cancer", "Renal Cell Carcinoma",
        "Bladder Cancer", "Prostate Cancer", "Testicular Cancer", "Ovarian Cancer", "Cervical Cancer",
        "Uterine Cancer", "Endometrial Cancer", "Thyroid Cancer", "Head and Neck Cancer", "Oral Cancer",
        "Laryngeal Cancer", "Nasopharyngeal Cancer", "Lymphoma", "Hodgkin Lymphoma", "Non-Hodgkin Lymphoma",
        "Multiple Myeloma", "Bone Cancer", "Osteosarcoma", "Ewing Sarcoma", "Soft Tissue Sarcoma",
        "Metastatic Cancer", "Secondary Cancer", "Carcinoma In Situ", "Tumor", "Neoplasm", "Malignancy",

        # Eye, Ear, Skin - Expanded
        "Cataract", "Glaucoma", "Open Angle Glaucoma", "Angle Closure Glaucoma", "Macular Degeneration",
        "AMD", "Retinal Detachment", "Diabetic Retinopathy", "Retinopathy", "Uveitis", "Conjunctivitis",
        "Dry Eye Syndrome", "Keratoconus", "Strabismus", "Amblyopia", "Color Blindness", "Night Blindness",
        "Hearing Loss", "Sensorineural Hearing Loss", "Conductive Hearing Loss", "Tinnitus", "Meniere's Disease",
        "Otosclerosis", "Vertigo", "Benign Paroxysmal Positional Vertigo", "BPPV", "Labyrinthitis",
        "Eczema", "Atopic Dermatitis", "Contact Dermatitis", "Seborrheic Dermatitis", "Dandruff",
        "Seborrheic Dermatitis", "Psoriasis", "Vitiligo", "Alopecia Areata", "Androgenetic Alopecia",
        "Rosacea", "Acne", "Acne Vulgaris", "Cystic Acne", "Folliculitis", "Impetigo", "Cellulitis",
        "Erysipelas", "Shingles", "Herpes Zoster", "Cold Sores", "Herpes Simplex", "Warts", "Moles",
        "Melanoma", "Basal Cell Carcinoma", "Squamous Cell Carcinoma", "Actinic Keratosis", "Seborrheic Keratosis",

        # Additional Conditions
        "Gout", "Hyperuricemia", "Kidney Disease", "Nephritis", "Glomerulonephritis", "Nephrotic Syndrome",
        "Acute Kidney Injury", "AKI", "Chronic Kidney Disease", "CKD", "End Stage Renal Disease", "ESRD",
        "Liver Disease", "Hepatitis", "Cirrhosis", "Liver Failure", "Acute Liver Failure", "Chronic Liver Disease",
        "Wilson's Disease", "Hemochromatosis", "Primary Biliary Cirrhosis", "PBC", "Primary Sclerosing Cholangitis",
        "PSC", "Autoimmune Hepatitis", "Non-Alcoholic Fatty Liver Disease", "NAFLD", "Alcoholic Liver Disease",
        "Gallbladder Disease", "Cholecystitis", "Cholangitis", "Pancreatic Disease", "Chronic Pancreatitis",
        "Cystic Fibrosis", "Pancreatic Insufficiency", "Inflammatory Bowel Disease", "IBD", "Crohn's Disease",
        "Ulcerative Colitis", "Diverticulitis", "Diverticulosis", "Celiac Disease", "Gluten Intolerance",
        "Lactose Intolerance", "Food Allergy", "Peanut Allergy", "Shellfish Allergy", "Drug Allergy",
        "Anaphylaxis", "Angioedema", "Urticaria", "Contact Dermatitis", "Atopic Dermatitis",
        "Autoimmune Disease", "Rheumatoid Arthritis", "Systemic Lupus Erythematosus", "SLE", "Sjogren's Syndrome",
        "Scleroderma", "Dermatomyositis", "Polymyositis", "Vasculitis", "Giant Cell Arteritis",
        "Temporal Arteritis", "Wegener's Granulomatosis", "Polyarteritis Nodosa", "Behcet's Disease",
        "Sarcoidosis", "Amyloidosis", "Hemochromatosis", "Wilson's Disease", "Gaucher's Disease",
        "Fabry Disease", "Porphyria", "Metabolic Syndrome", "Insulin Resistance", "PCOS",
        "Addison's Disease", "Cushing's Syndrome", "Pheochromocytoma", "Hyperparathyroidism",
        "Hypoparathyroidism", "Adrenal Insufficiency", "Pituitary Tumor", "Prolactinoma", "Acromegaly",
        "Growth Hormone Deficiency", "Diabetes Insipidus", "SIADH", "Syndrome of Inappropriate ADH",
        "Thyroid Nodule", "Goiter", "Thyroiditis", "Hashimoto's Thyroiditis", "Graves' Disease",
        "Blood Disorders", "Anemia", "Iron Deficiency Anemia", "Vitamin B12 Deficiency", "Folate Deficiency",
        "Hemolytic Anemia", "Aplastic Anemia", "Sickle Cell Anemia", "Thalassemia", "Hemophilia",
        "Von Willebrand Disease", "Thrombocytopenia", "ITP", "Immune Thrombocytopenic Purpura",
        "Hemolytic Uremic Syndrome", "HUS", "Thrombotic Thrombocytopenic Purpura", "TTP",
        "Disseminated Intravascular Coagulation", "DIC", "Deep Vein Thrombosis", "DVT",
        "Pulmonary Embolism", "PE", "Factor V Leiden", "Protein C Deficiency", "Protein S Deficiency",
        "Antiphospholipid Syndrome", "APS", "Polycythemia Vera", "Essential Thrombocythemia",
        "Myelofibrosis", "Leukemia", "Lymphoma", "Multiple Myeloma", "Waldenstrom Macroglobulinemia"
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
        # First, extract using predefined patterns
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
        
        # Generic pattern to catch any test name with value (for tests not in predefined list)
        # Look for common medical report table formats:
        # 1. Test Name: value unit
        # 2. Test Name - value unit  
        # 3. Test Name value unit (on same line)
        # 4. Test Name (newline) value unit
        
        # Common words to skip (not test names)
        skip_words = {'page', 'date', 'time', 'report', 'patient', 'doctor', 'lab', 'laboratory', 
                      'normal', 'range', 'reference', 'value', 'result', 'test', 'name', 'id',
                      'age', 'gender', 'male', 'female', 'years', 'old', 'mm', 'dd', 'yyyy',
                      'header', 'footer', 'page', 'of', 'total'}
        
        # Pattern 1: Test Name: value unit or Test Name - value unit
        generic_pattern1 = r'(?i)^([A-Z][A-Za-z0-9\s\-/\(\)]{2,40}?)\s*[:\-]\s*(\d+[.,]?\d*)\s*([a-zA-Z/%°µ²³]+)?'
        
        # Pattern 2: Test Name followed by value on same line (common in tables)
        generic_pattern2 = r'(?i)^([A-Z][A-Za-z0-9\s\-/\(\)]{2,40}?)\s+(\d+[.,]?\d*)\s+([a-zA-Z/%°µ²³]+)?\s*$'
        
        lines = text.split('\n')
        captured_tests = set(results.keys())
        
        # Process each line looking for test patterns
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or len(line) < 5:
                continue
            
            # Try pattern 1 (with colon or dash)
            match1 = re.match(generic_pattern1, line)
            if match1:
                test_name = match1.group(1).strip()
                value_str = match1.group(2).replace(",", "").strip()
                unit = match1.group(3).strip() if match1.group(3) else ""
                
                if self._is_valid_test_name(test_name, skip_words, captured_tests):
                    try:
                        value = float(value_str)
                        if 0 <= value <= 10000:
                            normalized_name = self._normalize_test_name(test_name)
                            if normalized_name not in results:
                                results[normalized_name].append({"value": value, "unit": unit})
                                captured_tests.add(normalized_name)
                    except (ValueError, AttributeError):
                        continue
            
            # Try pattern 2 (space-separated, common in tables)
            match2 = re.match(generic_pattern2, line)
            if match2:
                test_name = match2.group(1).strip()
                value_str = match2.group(2).replace(",", "").strip()
                unit = match2.group(3).strip() if match2.group(3) else ""
                
                if self._is_valid_test_name(test_name, skip_words, captured_tests):
                    try:
                        value = float(value_str)
                        if 0 <= value <= 10000:
                            normalized_name = self._normalize_test_name(test_name)
                            if normalized_name not in results:
                                results[normalized_name].append({"value": value, "unit": unit})
                                captured_tests.add(normalized_name)
                    except (ValueError, AttributeError):
                        continue
            
            # Also check if next line has a value (test name on one line, value on next)
            if i < len(lines) - 1:
                next_line = lines[i + 1].strip()
                value_match = re.match(r'^(\d+[.,]?\d*)\s+([a-zA-Z/%°µ²³]+)?', next_line)
                if value_match and self._is_valid_test_name(line, skip_words, captured_tests):
                    value_str = value_match.group(1).replace(",", "").strip()
                    unit = value_match.group(2).strip() if value_match.group(2) else ""
                    try:
                        value = float(value_str)
                        if 0 <= value <= 10000:
                            normalized_name = self._normalize_test_name(line)
                            if normalized_name not in results:
                                results[normalized_name].append({"value": value, "unit": unit})
                                captured_tests.add(normalized_name)
                    except (ValueError, AttributeError):
                        continue
        
        return dict(results)
    
    def _is_valid_test_name(self, test_name: str, skip_words: set, captured_tests: set) -> bool:
        """Check if a test name is valid and should be extracted"""
        if len(test_name) < 2 or len(test_name) > 50:
            return False
        if any(skip_word in test_name.lower() for skip_word in skip_words):
            return False
        # Check against captured tests (case-insensitive)
        normalized_check = self._normalize_test_name(test_name)
        if any(normalized_check.lower() == ct.lower() for ct in captured_tests):
            return False
        # Check if it looks like a test name (has letters, not just numbers)
        if not re.search(r'[A-Za-z]', test_name):
            return False
        return True
    
    def _normalize_test_name(self, test_name: str) -> str:
        """Normalize test name to standard format"""
        # Remove extra spaces
        normalized = ' '.join(test_name.split())
        # Capitalize properly (Title Case but preserve acronyms)
        words = normalized.split()
        normalized_words = []
        for word in words:
            if word.isupper() and len(word) > 1:
                # Preserve acronyms like "RBC", "WBC", "HDL", etc.
                normalized_words.append(word)
            else:
                normalized_words.append(word.title())
        return ' '.join(normalized_words)

    
    
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
    
    

    def _extract_diseases(self, doc) -> List[str]:
        """Extract disease entities with optimized pattern matching"""
        diseases = set()
        
        # Method 1: Extract from spaCy entities (if medspacy is available)
        for ent in doc.ents:
            if ent.label_ == "DISEASE" or "CONDITION" in ent.label_:
                normalized = self._normalize_disease(ent.text)
                if normalized and len(normalized) > 2:
                    diseases.add(normalized)
        
        # Method 2: Fast regex pattern matching
        text_lower = doc.text.lower()
        for pattern in self.disease_patterns:
            matches = pattern.findall(text_lower)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match else ""
                if match:
                    normalized = self._normalize_disease(match)
                    if normalized:
                        diseases.add(normalized)
        
        # Method 3: Direct vocabulary lookup for common terms
        words = set(re.findall(r'\b\w{4,}\b', text_lower))
        for word in words:
            if word in {d.lower() for d in self.diseases}:
                diseases.add(next(d for d in self.diseases if d.lower() == word))
        
        return sorted(diseases)
    
    def _extract_medicines(self, text: str) -> List[Dict[str, str]]:
        """Fast medicine extraction using patterns and fuzzy matching"""
        medicines = []
        text_lower = text.lower()
        
        # Pattern-based extraction
        for pattern in self.medicine_patterns:
            matches = pattern.finditer(text)
            for match in matches:
                med_name = match.group(1)
                normalized = self._normalize_medicine(med_name)
                
                # Extract dose if present
                dose_match = re.search(r'(\d+\s*(?:mg|mcg|ml|g|units?))', text[match.end():match.end()+50], re.I)
                dose = dose_match.group(1) if dose_match else ""
                
                medicines.append({
                    "name": normalized,
                    "original": med_name,
                    "dose": dose
                })
        
        # Also check for common medicine patterns
        med_pattern = re.compile(r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\s+(\d+\s*(?:mg|mcg|ml))', re.I)
        for match in med_pattern.finditer(text):
            med_name = match.group(1)
            dose = match.group(2)
            normalized = self._normalize_medicine(med_name)
            if normalized and normalized not in [m["name"] for m in medicines]:
                medicines.append({
                    "name": normalized,
                    "original": med_name,
                    "dose": dose
                })
        
        return medicines


    def _extract_key_findings(self, text: str) -> str:
        """Extract impression/findings section with improved regex"""
        findings_match = re.search(
            r"(IMPRESSION|FINDINGS|CONCLUSION|OPINION)[:\s]*(.*?)(?=\n\n|\Z)", 
            text, re.IGNORECASE | re.DOTALL)
        return findings_match.group(2).strip() if findings_match else ""

    def _extract_recommendations(self, doc) -> List[str]:
        """Fast recommendation extraction using multiple methods"""
        recommendations = set()
        text = doc.text
        
        # Method 1: Pattern-based extraction (fastest)
        for pattern in self.recommendation_patterns:
            matches = pattern.finditer(text)
            for match in matches:
                rec_text = match.group(1).strip()
                if len(rec_text) > 10 and len(rec_text) < 200:
                    recommendations.add(rec_text)
        
        # Method 2: Sentence-based extraction - expanded keywords
        rec_keywords = {
            "recommend", "suggest", "advise", "prescribe", "should", "must", "need to",
            "follow", "continue", "maintain", "keep", "take", "use", "apply",
            "avoid", "do not", "don't", "refrain", "stop", "discontinue",
            "monitor", "check", "test", "measure", "track", "watch",
            "increase", "decrease", "reduce", "limit", "restrict", "modify",
            "exercise", "physical activity", "workout", "fitness", "yoga", "walking",
            "diet", "nutrition", "food", "meal", "eat", "consume", "intake",
            "rest", "sleep", "hydration", "water", "fluids", "drink",
            "consult", "see", "visit", "meet", "contact", "call", "refer",
            "emergency", "urgent", "immediate", "asap", "right away",
            "prevent", "prevention", "protect", "protection",
            "treatment", "therapy", "medication", "medicine", "drug",
            "follow-up", "followup", "re-visit", "return", "next appointment",
            "schedule", "book", "appointment"
        }
        for sent in doc.sents:
            sent_lower = sent.text.lower()
            if any(keyword in sent_lower for keyword in rec_keywords):
                clean_sent = sent.text.strip()
                if len(clean_sent) > 15 and len(clean_sent) < 300:
                    recommendations.add(clean_sent)
        
        # Method 3: Extract from common sections
        sections = [
            (r'(?:recommendation|advice|suggestion|follow.?up)[:\s]+(.*?)(?=\n\n|\Z)', re.I | re.DOTALL),
            (r'(?:plan|treatment plan|management)[:\s]+(.*?)(?=\n\n|\Z)', re.I | re.DOTALL),
        ]
        for pattern, flags in sections:
            match = re.search(pattern, text, flags)
            if match:
                content = match.group(1).strip()
                # Split into sentences
                sentences = re.split(r'[\.!?]\s+', content)
                for sent in sentences:
                    if len(sent) > 15:
                        recommendations.add(sent.strip())
        
        return sorted(recommendations)
    
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
        """Optimized text processing with parallel extraction where possible"""
        # Process spaCy doc once
        doc = self.nlp(text)
        
        # Extract in parallel for faster processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                'diseases': executor.submit(self._extract_diseases, doc),
                'measurements': executor.submit(self._extract_measurements, text),
                'medicines': executor.submit(self._extract_medicines, text),
                'findings': executor.submit(self._extract_key_findings, text),
                'recommendations': executor.submit(self._extract_recommendations, doc),
                'specialization': executor.submit(self._predict_specialization, doc)
            }
            
            # Wait for all to complete
            results = {key: future.result() for key, future in futures.items()}
        
        analysis = {
            "measurements": results['measurements'],
            "diseases": results['diseases'],
            "medications": results['medicines'],
            "specialization": results['specialization'],
            "findings": results['findings'],
            "recommendations": results['recommendations']
        }

        return analysis
