# text_analyzer.py - Medical text analysis and NLP processing
import boto3
import re
from rapidfuzz import process, fuzz

COMMON_FIXES = {
    # --- Medicines (Neurology, Oncology, General) ---
    r'\bLeven?fil\b': 'Levipil',
    r'\bLevepil\b': 'Levipil',
    r'\bLevitol\b': 'Levipil',
    r'\bTrexayey\b': 'Taxol',
    r'\bTaxzol\b': 'Taxol',
    r'\bTaxoil\b': 'Taxol',
    r'\bTAchoc\b': 'TDK 44',
    r'\bT\s*Komin\s*D3\b': 'Homium D',
    r'\bTpomin\b': 'Homium D',
    r'\bTiloba\b': 'Floba',
    r'\bFlova\b': 'Floba',
    r'\bFlooba\b': 'Floba',
    r'\bxpodary\b': 'Taxol',
    r'\bTaxoll?\b': 'Taxol',
    r'\bxx\b': '',
    r'\bAmlo\b': 'Amlodipine',
    r'\bAmlof\b': 'Amlodipine',
    r'\bAmlodep\b': 'Amlodipine',
    r'\bAtor\b': 'Atorvastatin',
    r'\bAtrovast\b': 'Atorvastatin',
    r'\bAtorva\b': 'Atorvastatin',
    r'\bEcospriin?\b': 'Ecosprin',
    r'\bEcosprin\b': 'Ecosprin',
    r'\bMetfor\b': 'Metformin',
    r'\bMetforin\b': 'Metformin',
    r'\bMetmorf\b': 'Metformin',
    r'\bGlycomet\b': 'Metformin',
    r'\bPantaprazole\b': 'Pantoprazole',
    r'\bPantaprozole\b': 'Pantoprazole',
    r'\bPantazol\b': 'Pantoprazole',
    r'\bOmiz\b': 'Omeprazole',
    r'\bOmizol\b': 'Omeprazole',
    r'\bOmez\b': 'Omeprazole',
    r'\bParacetmol\b': 'Paracetamol',
    r'\bParacetemol\b': 'Paracetamol',
    r'\bParacitamol\b': 'Paracetamol',
    r'\bDolo\b': 'Paracetamol',
    r'\bCrozit\b': 'Crozit',
    r'\bAugmantin\b': 'Augmentin',
    r'\bAmoxyclav\b': 'Augmentin',
    r'\bAmoxycilin\b': 'Amoxicillin',
    r'\bAmoxillin\b': 'Amoxicillin',
    r'\bAzit\b': 'Azithromycin',
    r'\bAzitromicin\b': 'Azithromycin',
    r'\bAzitral\b': 'Azithromycin',
    r'\bCefix\b': 'Cefixime',
    r'\bCefixim\b': 'Cefixime',
    r'\bCefiximee\b': 'Cefixime',

    # --- Conditions ---
    r'\bParaphysical\b': 'Pharyngeal',
    r'\bCarcinoma\b': 'Carcinoma',
    r'\bMetts\b': 'Metastases',
    r'\bMetases\b': 'Metastases',
    r'\bNafecal Sign\b': 'No Focal Sign',
    r'\bNofocal\b': 'No Focal Sign',
    r'\bDiabities\b': 'Diabetes',
    r'\bDiabetees\b': 'Diabetes',
    r'\bHypertention\b': 'Hypertension',
    r'\bHypertenion\b': 'Hypertension',
    r'\bTuberclosis\b': 'Tuberculosis',
    r'\bTB\b': 'Tuberculosis',
    r'\bAsthama\b': 'Asthma',
    r'\bAsthamaic\b': 'Asthma',

    # --- Tests / Procedures ---
    r'\bE\.E\.G\b': 'EEG',
    r'\bEEGG\b': 'EEG',
    r'\bE\.M\.G\b': 'EMG',
    r'\bNCVV?\b': 'NCV',
    r'\bV\.E\.P\b': 'VEP',
    r'\bB\.E\.R\.A\b': 'BERA',
    r'\bN\.T\.R\.E\b': 'NTRE',
    r'\bPETCT\b': 'PET-CT',
    r'\bPet Scan\b': 'PET-CT',
    r'\bCT Scan\b': 'CT-Scan',
    r'\bMRI Scan\b': 'MRI',
    r'\bXray\b': 'X-Ray',
    r'\bX Ray\b': 'X-Ray',
    r'\bSonograpy\b': 'Sonography',
    # --- Neurology Medicines ---
    r'\bLeven?fil\b': 'Levipil',
    r'\bLevepil\b': 'Levipil',
    r'\bLevipl\b': 'Levipil',
    r'\bLevapil\b': 'Levipil',
    r'\bLupinil\b': 'Levipil',

    # --- Oncology Medicines ---
    r'\bTrexayey\b': 'Taxol',
    r'\bTaxoil\b': 'Taxol',
    r'\bTaxoll?\b': 'Taxol',
    r'\bTacsul\b': 'Taxol',
    r'\bPactol\b': 'Paclitaxel',
    r'\bDocetxel\b': 'Docetaxel',
    r'\bDocetazol\b': 'Docetaxel',

    # --- Supplements / Vitamins ---
    r'\bT\s*Komin\s*D3\b': 'Homium D',
    r'\bTpomin\b': 'Homium D',
    r'\bTpomin D\b': 'Homium D',
    r'\bTpomin D3\b': 'Homium D',
    r'\bTiloba\b': 'Floba',
    r'\bFlooba\b': 'Floba',
    r'\bFlova\b': 'Floba',

    # --- Other Medicines (Common in India) ---
    r'\bMetfor\b': 'Metformin',
    r'\bMetforin\b': 'Metformin',
    r'\bMetmorf\b': 'Metformin',
    r'\bGlycomet\b': 'Metformin',
    r'\bAmlodep\b': 'Amlodipine',
    r'\bAmlo\b': 'Amlodipine',
    r'\bAmlof\b': 'Amlodipine',
    r'\bAtorva\b': 'Atorvastatin',
    r'\bAtrovast\b': 'Atorvastatin',
    r'\bAtrosat\b': 'Atorvastatin',
    r'\bEcospriin?\b': 'Ecosprin',
    r'\bEcosprin\b': 'Ecosprin',
    r'\bAspiriin\b': 'Aspirin',
    r'\bAsporin\b': 'Aspirin',
    r'\bClopidogrll?\b': 'Clopidogrel',
    r'\bClopidogil\b': 'Clopidogrel',
    r'\bClopidoral\b': 'Clopidogrel',

    # --- Painkillers / Fever ---
    r'\bParacetmol\b': 'Paracetamol',
    r'\bParacetemol\b': 'Paracetamol',
    r'\bParacitamol\b': 'Paracetamol',
    r'\bParacitamyl\b': 'Paracetamol',
    r'\bDolo\b': 'Paracetamol',
    r'\bCrocin\b': 'Paracetamol',

    # --- Antibiotics ---
    r'\bAugmantin\b': 'Augmentin',
    r'\bAmoxyclav\b': 'Augmentin',
    r'\bAmoxycilin\b': 'Amoxicillin',
    r'\bAmoxillin\b': 'Amoxicillin',
    r'\bAmoxil\b': 'Amoxicillin',
    r'\bAzit\b': 'Azithromycin',
    r'\bAzitral\b': 'Azithromycin',
    r'\bAzitromicin\b': 'Azithromycin',
    r'\bCefixim\b': 'Cefixime',
    r'\bCefiximee\b': 'Cefixime',
    r'\bCefexim\b': 'Cefixime',
    r'\bCeftriaxon\b': 'Ceftriaxone',
    r'\bCeftriax\b': 'Ceftriaxone',

    # --- GI Medicines ---
    r'\bPantaprazole\b': 'Pantoprazole',
    r'\bPantaprozole\b': 'Pantoprazole',
    r'\bPantazol\b': 'Pantoprazole',
    r'\bPantodac\b': 'Pantoprazole',
    r'\bOmiz\b': 'Omeprazole',
    r'\bOmizol\b': 'Omeprazole',
    r'\bOmez\b': 'Omeprazole',
    r'\bRabeprazol\b': 'Rabeprazole',
    r'\bRabezole\b': 'Rabeprazole',

    # --- Conditions ---
    r'\bParaphysical\b': 'Pharyngeal',
    r'\bCarcinomaa?\b': 'Carcinoma',
    r'\bMetts\b': 'Metastases',
    r'\bMetases\b': 'Metastases',
    r'\bNafecal Sign\b': 'No Focal Sign',
    r'\bNofocal\b': 'No Focal Sign',
    r'\bDiabities\b': 'Diabetes',
    r'\bDiabetees\b': 'Diabetes',
    r'\bHypertention\b': 'Hypertension',
    r'\bHypertenion\b': 'Hypertension',
    r'\bTuberclosis\b': 'Tuberculosis',
    r'\bTuberculasis\b': 'Tuberculosis',
    r'\bAsthama\b': 'Asthma',
    r'\bAsthamma\b': 'Asthma',

    # --- Tests / Procedures ---
    r'\bE\.E\.G\b': 'EEG',
    r'\bEEGG\b': 'EEG',
    r'\bE\.M\.G\b': 'EMG',
    r'\bEMGG\b': 'EMG',
    r'\bNCVV?\b': 'NCV',
    r'\bV\.E\.P\b': 'VEP',
    r'\bB\.E\.R\.A\b': 'BERA',
    r'\bN\.T\.R\.E\b': 'NTRE',
    r'\bPet Scan\b': 'PET-CT',
    r'\bPETCT\b': 'PET-CT',
    r'\bCT Scan\b': 'CT-Scan',
    r'\bC\.T\. Scan\b': 'CT-Scan',
    r'\bMRI Scan\b': 'MRI',
    r'\bMR I\b': 'MRI',
    r'\bXray\b': 'X-Ray',
    r'\bX Ray\b': 'X-Ray',
    r'\bSonograpy\b': 'Sonography',
    r'\bUltrasond\b': 'Ultrasound',
    r'\bUltrasonik\b': 'Ultrasound',

    # --- General terms ---
    r'\bxx\b': '',
    r'\bRx\b': 'Prescription',
    r'\bSyp\b': 'Syrup',
    r'\bTab\b': 'Tablet',
    r'\bCap\b': 'Capsule',
    r'\bInj\b': 'Injection',
    r'\bOint\b': 'Ointment',
    # --- Dose & Units Errors ---
    r'\bmgm\b': 'mg',         # mgm → mg
    r'\bmc gm\b': 'mcg',      # mc gm → mcg
    r'\bmlt\b': 'ml',         # mlt → ml
    r'\bmicc?g\b': 'mcg',     # micg/micc → mcg
    r'\bMGS\b': 'mg',         # MGS → mg
    r'\bmcgm\b': 'mcg',
    r'\bgrms?\b': 'g',        # grm / grms → g
    r'\bIU\b': 'IU',          # normalize IU

    # --- Frequency & Timing ---
    r'\bBD\b': '2 times daily',
    r'\bTDS\b': '3 times daily',
    r'\bQID\b': '4 times daily',
    r'\bOD\b': 'once daily',
    r'\bHS\b': 'at bedtime',
    r'\bSOS\b': 'if needed',
    r'\bQHS\b': 'at night',
    r'\bSTAT\b': 'immediately',
    r'\bQOD\b': 'every other day',
    r'\bQWK\b': 'once weekly',

    # --- Prescription Symbols ---
    r'\bRx\b': 'Prescription',
    r'\bSyp\b': 'Syrup',
    r'\bTab\b': 'Tablet',
    r'\bCap\b': 'Capsule',
    r'\bInj\b': 'Injection',
    r'\bOint\b': 'Ointment',
    r'\bDrp\b': 'Drops',
    r'\bSoln\b': 'Solution',
    r'\bSusp\b': 'Suspension',

    # --- Disease Short Forms ---
    r'\bHTN\b': 'Hypertension',
    r'\bDM\b': 'Diabetes Mellitus',
    r'\bCOPD\b': 'Chronic Obstructive Pulmonary Disease',
    r'\bCKD\b': 'Chronic Kidney Disease',
    r'\bCLD\b': 'Chronic Liver Disease',
    r'\bRA\b': 'Rheumatoid Arthritis',
    r'\bOA\b': 'Osteoarthritis',
    r'\bTB\b': 'Tuberculosis',
    r'\bCA\b': 'Carcinoma',
    r'\bAML\b': 'Acute Myeloid Leukemia',

    # --- Test Name OCR Errors (rare) ---
    r'\bHB1C\b': 'HbA1c',
    r'\bHBAIC\b': 'HbA1c',
    r'\bThyroid Proflie\b': 'Thyroid Profile',
    r'\bLFTS\b': 'LFT',
    r'\bKFTS\b': 'KFT',
    r'\bRFTS\b': 'RFT',
    r'\bECHO\b': 'Echo',
    r'\bEchocardiagram\b': 'Echocardiogram',
    r'\bDoplr\b': 'Doppler',
    r'\bUrin\b': 'Urine',

    # --- Common OCR Misreads (General) ---
    r'\bBp\b': 'BP',
    r'\bPR\b': 'Pulse Rate',
    r'\bTemp\b': 'Temperature',
    r'\bWt\b': 'Weight',
    r'\bHt\b': 'Height',
    r'\bSpO\b': 'SpO2',
    r'\bSPO2\b': 'SpO2',
}
REFERENCE_TERMS = [
    # --- Medicines (Common in prescriptions) ---
    "Levipil", "Taxol", "Floba", "Homium D",
    "Paracetamol", "Dolo", "Crocin",
    "Amlodipine", "Atorvastatin", "Metformin",
    "Pantoprazole", "Omeprazole", "Rabeprazole",
    "Azithromycin", "Cefixime", "Ceftriaxone",
    "Augmentin", "Amoxicillin", "Clopidogrel",
    "Ecosprin", "Aspirin", "Insulin", "Metoprolol",
    "Losartan", "Telmisartan", "Ramipril",
    "Levothyroxine", "Prednisolone", "Hydroxychloroquine",
    "Chloroquine", "Remdesivir", "Favipiravir",
    "Dexamethasone", "Hydrocortisone", "Methylprednisolone",
    "Cetirizine", "Levocetirizine", "Fexofenadine",
    "Montelukast", "Salbutamol", "Budesonide",
    "Formoterol", "Tiotropium", "Theophylline",
    "Glibenclamide", "Glimepiride", "Gliclazide",
    "Sitagliptin", "Vildagliptin", "Linagliptin",
    "Pioglitazone", "Canagliflozin", "Dapagliflozin",
    "Empagliflozin", "Rosuvastatin", "Simvastatin",
    "Ezetimibe", "Fenofibrate", "Gemfibrozil",
    "Atenolol", "Bisoprolol", "Propranolol",
    "Carvedilol", "Nebivolol", "Digoxin",
    "Furosemide", "Spironolactone", "Amiodarone",
    "Warfarin", "Heparin", "Enoxaparin",
    "Apixaban", "Rivaroxaban", "Dabigatran",
    "Nitroglycerin", "Isosorbide Mononitrate", "Ranolazine",
    "Ivabradine", "Amoxiclav", "Ciprofloxacin",
    "Ofloxacin", "Levofloxacin", "Moxifloxacin",
    "Doxycycline", "Tetracycline", "Minocycline",
    "Linezolid", "Vancomycin", "Teicoplanin",
    "Meropenem", "Imipenem", "Cefuroxime",
    "Clarithromycin", "Erythromycin", "Metronidazole",
    "Tinidazole", "Albendazole", "Ivermectin",
    "Praziquantel", "Artemisinin", "Artemether",
    "Lumefantrine", "Quinine", "Chloramphenicol",

    # --- Conditions / Diseases ---
    "Metastases", "No Focal Sign", "Pharyngeal Carcinoma", "Carcinoma",
    "Diabetes", "Hypertension", "Tuberculosis", "Asthma",
    "Chronic Kidney Disease", "Chronic Liver Disease",
    "Rheumatoid Arthritis", "Osteoarthritis", "Migraine",
    "Epilepsy", "Stroke", "Seizure Disorder",
    "Depression", "Anxiety Disorder", "Parkinson's Disease",
    "Alzheimer's Disease", "Multiple Sclerosis", "Brain Tumor",
    "Cervical Cancer", "Breast Cancer", "Lung Cancer",
    "Prostate Cancer", "Leukemia", "Lymphoma",
    "Gastric Ulcer", "Peptic Ulcer", "GERD",
    "IBS", "Crohn's Disease", "Ulcerative Colitis",
    "Hepatitis B", "Hepatitis C", "Cirrhosis",
    "COVID-19", "Pneumonia", "Bronchitis",
    "Sinusitis", "Otitis Media", "Tonsillitis",
    "Anemia", "Iron Deficiency", "Thalassemia",
    "Sickle Cell Disease", "Hemophilia", "Gout",
    "Psoriasis", "Eczema", "Vitiligo",

    # --- Tests / Procedures ---
    "EEG", "EMG", "NCV", "VEP", "BERA", "NTRE",
    "PET-CT", "CT-Scan", "MRI", "X-Ray", "Sonography",
    "Ultrasound", "Echocardiogram", "Doppler", "HbA1c",
    "LFT", "KFT", "RFT", "CBC", "Lipid Profile", "Thyroid Profile",
    "Blood Sugar", "Urine Test", "Blood Pressure", "Pulse Rate",
    "Temperature", "SpO2", "ECG", "Echo", "EEG Video",
    "Holter Monitoring", "Stress Test", "Angiography",
    "Angioplasty", "Biopsy", "FNAC",
    "Pap Smear", "Mammogram", "Colonoscopy",
    "Endoscopy", "Gastroscopy", "Bronchoscopy",
    "Laparoscopy", "Hysteroscopy", "IVP",
    "Barium Swallow", "Barium Enema", "Uroflowmetry",
    "PSA Test", "Troponin Test", "CRP",
    "ESR", "D-Dimer", "Blood Culture",

    # --- General Medical Terms ---
    "Prescription", "Tablet", "Capsule", "Syrup", "Injection",
    "Ointment", "Drops", "Solution", "Suspension",
    "Dose", "mg", "mcg", "ml", "IU",
    "once daily", "2 times daily", "3 times daily", "at bedtime",
    "if needed", "immediately", "every other day",
    "once weekly", "oral", "topical", "intravenous",
    "subcutaneous", "intramuscular", "infusion",
    "BP", "HR", "PR", "SpO2", "RR",
    "Wt", "Ht", "BMI", "Temp", "BSA",
    "Allergy", "Adverse Reaction", "Side Effect",
    "Contraindication", "Follow-up", "Referral",
    "Primary Care", "Specialist", "General Physician",
    "Neurologist", "Oncologist", "Cardiologist",
    "Endocrinologist", "Nephrologist", "Hepatologist",
    "Pulmonologist", "Orthopedic", "Dermatologist",
    "ENT Specialist", "Psychiatrist", "Physiotherapist"
]
# --- Step 3: Auto-correction pipeline ---
def auto_correct(text: str) -> str:
    """Apply common fixes + fuzzy matching to clean OCR output."""
    
    # Apply regex-based common fixes
    clean = text
    for pattern, replacement in COMMON_FIXES.items():
        clean = re.sub(pattern, replacement, clean, flags=re.IGNORECASE)

    # Fuzzy match against reference terms (if word still looks suspicious)
    words = clean.split()
    corrected_words = []
    for w in words:
        if not w.strip():
            continue
        # Fuzzy matching (score threshold = 85)
        result = process.extractOne(w, REFERENCE_TERMS, scorer=fuzz.ratio)
        if result and len(result) >= 2:
            match, score = result[0], result[1]
            if score >= 85:
                corrected_words.append(match)
            else:
                corrected_words.append(w)
        else:
            corrected_words.append(w)
    
    return " ".join(corrected_words)

def clean_ocr_text(text: str) -> str:
    # normalize spaces
    t = re.sub(r'[ \t]+', ' ', text)
    t = re.sub(r'\n{2,}', '\n', t)
    # common medical OCR fixes
    for pat, rep in COMMON_FIXES.items():
        t = re.sub(pat, rep, t, flags=re.IGNORECASE)
    return t.strip()

# --- extend in text_analyzer.py ---
MEDICATION_CANON = {
    # --- Basic / Commonly used ---
    "paracetamol": {"generic": "Paracetamol", "purpose": "Pain relief / Fever"},
    "dolo": {"generic": "Paracetamol", "purpose": "Pain relief / Fever"},
    "crocin": {"generic": "Paracetamol", "purpose": "Pain relief / Fever"},
    "combiflam": {"generic": "Ibuprofen + Paracetamol", "purpose": "Pain & inflammation"},
    "ibuprofen": {"generic": "Ibuprofen", "purpose": "Pain & inflammation"},
    "diclofenac": {"generic": "Diclofenac", "purpose": "Pain & arthritis"},
    "aceclofenac": {"generic": "Aceclofenac", "purpose": "Pain & arthritis"},
    "naproxen": {"generic": "Naproxen", "purpose": "Pain & inflammation"},
    

    # --- Antibiotics ---
    "amoxicillin": {"generic": "Amoxicillin", "purpose": "Antibiotic"},
    "augmentin": {"generic": "Amoxicillin + Clavulanic acid", "purpose": "Antibiotic"},
    "ampicillin": {"generic": "Ampicillin", "purpose": "Antibiotic"},
    "azithromycin": {"generic": "Azithromycin", "purpose": "Antibiotic"},
    "clarithromycin": {"generic": "Clarithromycin", "purpose": "Antibiotic"},
    "erythromycin": {"generic": "Erythromycin", "purpose": "Antibiotic"},
    "cefixime": {"generic": "Cefixime", "purpose": "Antibiotic"},
    "cefpodoxime": {"generic": "Cefpodoxime", "purpose": "Antibiotic"},
    "cefuroxime": {"generic": "Cefuroxime", "purpose": "Antibiotic"},
    "ceftriaxone": {"generic": "Ceftriaxone", "purpose": "Antibiotic (injection)"},
    "ceftazidime": {"generic": "Ceftazidime", "purpose": "Antibiotic"},
    "cefotaxime": {"generic": "Cefotaxime", "purpose": "Antibiotic"},
    "cefepime": {"generic": "Cefepime", "purpose": "Antibiotic"},
    "meropenem": {"generic": "Meropenem", "purpose": "Resistant infections"},
    "imipenem": {"generic": "Imipenem", "purpose": "Resistant infections"},
    "ertapenem": {"generic": "Ertapenem", "purpose": "Resistant infections"},
    "doripenem": {"generic": "Doripenem", "purpose": "Resistant infections"},
    "linezolid": {"generic": "Linezolid", "purpose": "MRSA / resistant infections"},
    "vancomycin": {"generic": "Vancomycin", "purpose": "MRSA / severe infections"},
    "teicoplanin": {"generic": "Teicoplanin", "purpose": "Resistant infections"},
    "tigecycline": {"generic": "Tigecycline", "purpose": "Resistant infections"},
    "colistin": {"generic": "Colistin", "purpose": "Resistant Gram-negative infections"},
    "polymyxin b": {"generic": "Polymyxin B", "purpose": "Resistant Gram-negative infections"},
    "ciprofloxacin": {"generic": "Ciprofloxacin", "purpose": "Antibiotic"},
    "ofloxacin": {"generic": "Ofloxacin", "purpose": "Antibiotic"},
    "levofloxacin": {"generic": "Levofloxacin", "purpose": "Antibiotic"},
    "moxifloxacin": {"generic": "Moxifloxacin", "purpose": "Antibiotic"},
    "norfloxacin": {"generic": "Norfloxacin", "purpose": "Antibiotic"},
    "gatifloxacin": {"generic": "Gatifloxacin", "purpose": "Antibiotic"},
    "doxycycline": {"generic": "Doxycycline", "purpose": "Antibiotic"},
    "minocycline": {"generic": "Minocycline", "purpose": "Antibiotic"},
    "tetracycline": {"generic": "Tetracycline", "purpose": "Antibiotic"},
    "chloramphenicol": {"generic": "Chloramphenicol", "purpose": "Antibiotic"},
    "clindamycin": {"generic": "Clindamycin", "purpose": "Antibiotic"},
    "metronidazole": {"generic": "Metronidazole", "purpose": "Anaerobic infections"},
    "tinidazole": {"generic": "Tinidazole", "purpose": "Anaerobic infections"},
    "nitrofurantoin": {"generic": "Nitrofurantoin", "purpose": "UTI"},
    "fosfomycin": {"generic": "Fosfomycin", "purpose": "UTI"},
    "piperacillin tazobactam": {"generic": "Piperacillin + Tazobactam", "purpose": "Broad-spectrum antibiotic"},
    "tazobactam": {"generic": "Tazobactam", "purpose": "Beta-lactamase inhibitor"},
    "sulbactam": {"generic": "Sulbactam", "purpose": "Beta-lactamase inhibitor"},
    "cefoperazone sulbactam": {"generic": "Cefoperazone + Sulbactam", "purpose": "Broad-spectrum antibiotic"},
    "aztreonam": {"generic": "Aztreonam", "purpose": "Gram-negative infections"},
    "gentamicin": {"generic": "Gentamicin", "purpose": "Aminoglycoside antibiotic"},
    "amikacin": {"generic": "Amikacin", "purpose": "Aminoglycoside antibiotic"},
    "tobramycin": {"generic": "Tobramycin", "purpose": "Aminoglycoside antibiotic"},
    "streptomycin": {"generic": "Streptomycin", "purpose": "Aminoglycoside antibiotic / TB"},
    "rifampicin": {"generic": "Rifampicin", "purpose": "TB / Antibiotic"},
    "isoniazid": {"generic": "Isoniazid", "purpose": "TB"},
    "ethambutol": {"generic": "Ethambutol", "purpose": "TB"},
    "pyrazinamide": {"generic": "Pyrazinamide", "purpose": "TB"},
    "dapsone": {"generic": "Dapsone", "purpose": "Leprosy / Antibiotic"},
    "co-trimoxazole": {"generic": "Trimethoprim + Sulfamethoxazole", "purpose": "Antibiotic"},
    "trimethoprim": {"generic": "Trimethoprim", "purpose": "Antibiotic"},
    "sulfamethoxazole": {"generic": "Sulfamethoxazole", "purpose": "Antibiotic"},

    # --- Diabetes ---
    "metformin": {"generic": "Metformin", "purpose": "Diabetes"},
    "glimepiride": {"generic": "Glimepiride", "purpose": "Diabetes"},
    "gliclazide": {"generic": "Gliclazide", "purpose": "Diabetes"},
    "sitagliptin": {"generic": "Sitagliptin", "purpose": "Diabetes"},
    "linagliptin": {"generic": "Linagliptin", "purpose": "Diabetes"},
    "dapagliflozin": {"generic": "Dapagliflozin", "purpose": "Diabetes"},
    "empagliflozin": {"generic": "Empagliflozin", "purpose": "Diabetes"},
    "insulin": {"generic": "Insulin", "purpose": "Diabetes control"},

    # --- Hypertension / Heart ---
    "amlodipine": {"generic": "Amlodipine", "purpose": "Hypertension"},
    "telmisartan": {"generic": "Telmisartan", "purpose": "Hypertension"},
    "losartan": {"generic": "Losartan", "purpose": "Hypertension"},
    "ramipril": {"generic": "Ramipril", "purpose": "Hypertension"},
    "atenolol": {"generic": "Atenolol", "purpose": "Hypertension"},
    "metoprolol": {"generic": "Metoprolol", "purpose": "Hypertension"},
    "bisoprolol": {"generic": "Bisoprolol", "purpose": "Heart failure"},
    "carvedilol": {"generic": "Carvedilol", "purpose": "Heart failure"},
    "furosemide": {"generic": "Furosemide", "purpose": "Diuretic (BP/CHF)"},
    "spironolactone": {"generic": "Spironolactone", "purpose": "Heart / CHF"},

    # --- Cholesterol ---
    "atorvastatin": {"generic": "Atorvastatin", "purpose": "Cholesterol"},
    "rosuvastatin": {"generic": "Rosuvastatin", "purpose": "Cholesterol"},
    "simvastatin": {"generic": "Simvastatin", "purpose": "Cholesterol"},

    # --- Thyroid ---
    "eltroxin": {"generic": "Levothyroxine", "purpose": "Thyroid hormone replacement"},
    "thyronorm": {"generic": "Levothyroxine", "purpose": "Thyroid hormone replacement"},

    # --- Neuro / Epilepsy ---
    "levipil": {"generic": "Levetiracetam", "purpose": "Anti-seizure"},
    "valparin": {"generic": "Valproic Acid", "purpose": "Anti-seizure"},
    "oxetol": {"generic": "Oxcarbazepine", "purpose": "Anti-seizure"},
    "lamictal": {"generic": "Lamotrigine", "purpose": "Anti-seizure"},
    "tegretol": {"generic": "Carbamazepine", "purpose": "Anti-seizure"},
    "clobazam": {"generic": "Clobazam", "purpose": "Anti-seizure / Anxiety"},
    "diazepam": {"generic": "Diazepam", "purpose": "Anxiety / Seizure"},
    "clonazepam": {"generic": "Clonazepam", "purpose": "Seizure / Anxiety"},

    # --- Oncology / Chemotherapy ---
    "taxol": {"generic": "Paclitaxel", "purpose": "Chemotherapy"},
    "cisplatin": {"generic": "Cisplatin", "purpose": "Chemotherapy"},
    "carboplatin": {"generic": "Carboplatin", "purpose": "Chemotherapy"},
    "docetaxel": {"generic": "Docetaxel", "purpose": "Chemotherapy"},
    "cyclophosphamide": {"generic": "Cyclophosphamide", "purpose": "Chemotherapy"},
    "doxorubicin": {"generic": "Doxorubicin", "purpose": "Chemotherapy"},
    "imatinib": {"generic": "Imatinib", "purpose": "Targeted therapy (CML)"},
    "gefitinib": {"generic": "Gefitinib", "purpose": "Targeted therapy (Lung cancer)"},
    "rituximab": {"generic": "Rituximab", "purpose": "Immunotherapy"},
    "nivolumab": {"generic": "Nivolumab", "purpose": "Immunotherapy"},

    # --- Steroids & Anti-inflammatory ---
    "prednisolone": {"generic": "Prednisolone", "purpose": "Steroid (inflammation)"},
    "hydrocortisone": {"generic": "Hydrocortisone", "purpose": "Steroid"},
    "dexamethasone": {"generic": "Dexamethasone", "purpose": "Steroid"},
    "methylprednisolone": {"generic": "Methylprednisolone", "purpose": "Steroid"},

    # --- Supplements ---
    "vitamin d": {"generic": "Cholecalciferol", "purpose": "Supplement"},
    "homium d": {"generic": "Vitamin D (approx.)", "purpose": "Supplement"},
    "vitamin b12": {"generic": "Cyanocobalamin", "purpose": "Supplement"},
    "folic acid": {"generic": "Folic Acid", "purpose": "Supplement"},
    "iron": {"generic": "Ferrous Sulfate", "purpose": "Anemia treatment"},
    "calcium": {"generic": "Calcium Carbonate", "purpose": "Supplement"},
    "zinc": {"generic": "Zinc Sulfate", "purpose": "Supplement"},
    # --- Anti-fungal ---
    "fluconazole": {"generic": "Fluconazole", "purpose": "Antifungal"},
    "itraconazole": {"generic": "Itraconazole", "purpose": "Antifungal"},
    "voriconazole": {"generic": "Voriconazole", "purpose": "Antifungal"},
    "amphotericin b": {"generic": "Amphotericin B", "purpose": "Severe fungal infections"},

    # --- Anti-viral ---
    "acyclovir": {"generic": "Acyclovir", "purpose": "Antiviral (Herpes, Chickenpox)"},
    "valacyclovir": {"generic": "Valacyclovir", "purpose": "Antiviral (Herpes, Shingles)"},
    "remdesivir": {"generic": "Remdesivir", "purpose": "Antiviral (COVID-19)"},
    "oseltamivir": {"generic": "Oseltamivir", "purpose": "Antiviral (Influenza)"},
    "tenofovir": {"generic": "Tenofovir", "purpose": "Antiviral (HIV, Hepatitis B)"},
    "lamivudine": {"generic": "Lamivudine", "purpose": "Antiviral (HIV, Hepatitis B)"},

    # --- Anti-malarial ---
    "chloroquine": {"generic": "Chloroquine", "purpose": "Antimalarial"},
    "hydroxychloroquine": {"generic": "Hydroxychloroquine", "purpose": "Antimalarial / RA"},
    "artesunate": {"generic": "Artesunate", "purpose": "Severe Malaria"},
    "artemether": {"generic": "Artemether", "purpose": "Malaria"},
    "lumefantrine": {"generic": "Lumefantrine", "purpose": "Malaria"},

    # --- TB Drugs ---
    "isoniazid": {"generic": "Isoniazid", "purpose": "Tuberculosis"},
    "rifampicin": {"generic": "Rifampicin", "purpose": "Tuberculosis"},
    "pyrazinamide": {"generic": "Pyrazinamide", "purpose": "Tuberculosis"},
    "ethambutol": {"generic": "Ethambutol", "purpose": "Tuberculosis"},
    "streptomycin": {"generic": "Streptomycin", "purpose": "Tuberculosis"},

    # --- Psychiatric ---
    "sertraline": {"generic": "Sertraline", "purpose": "Depression / Anxiety"},
    "fluoxetine": {"generic": "Fluoxetine", "purpose": "Depression"},
    "escitalopram": {"generic": "Escitalopram", "purpose": "Depression / Anxiety"},
    "paroxetine": {"generic": "Paroxetine", "purpose": "Depression"},
    "venlafaxine": {"generic": "Venlafaxine", "purpose": "Depression / Anxiety"},
    "duloxetine": {"generic": "Duloxetine", "purpose": "Depression / Neuropathy"},
    "bupropion": {"generic": "Bupropion", "purpose": "Depression / Smoking cessation"},
    "olanzapine": {"generic": "Olanzapine", "purpose": "Schizophrenia / Bipolar"},
    "risperidone": {"generic": "Risperidone", "purpose": "Schizophrenia / Bipolar"},
    "quetiapine": {"generic": "Quetiapine", "purpose": "Schizophrenia / Bipolar"},
    "aripiprazole": {"generic": "Aripiprazole", "purpose": "Schizophrenia / Depression add-on"},

    # --- Dermatology ---
    "clobetasol": {"generic": "Clobetasol", "purpose": "Steroid cream (eczema, psoriasis)"},
    "betamethasone": {"generic": "Betamethasone", "purpose": "Steroid cream/injection"},
    "mupirocin": {"generic": "Mupirocin", "purpose": "Skin infection (topical antibiotic)"},
    "clotrimazole": {"generic": "Clotrimazole", "purpose": "Antifungal cream"},
    "ketoconazole": {"generic": "Ketoconazole", "purpose": "Antifungal cream/shampoo"},

    # --- Gastro / Stomach ---
    "domperidone": {"generic": "Domperidone", "purpose": "Acidity / Nausea"},
    "ondansetron": {"generic": "Ondansetron", "purpose": "Nausea / Vomiting"},
    "ranitidine": {"generic": "Ranitidine", "purpose": "Acidity (old use)"},
    "famotidine": {"generic": "Famotidine", "purpose": "Acidity"},
    "sucralfate": {"generic": "Sucralfate", "purpose": "Ulcer protection"},
    "mesalamine": {"generic": "Mesalamine", "purpose": "Ulcerative colitis / IBD"},

    # --- Respiratory / Asthma ---
    "salbutamol": {"generic": "Salbutamol", "purpose": "Asthma inhaler"},
    "formoterol": {"generic": "Formoterol", "purpose": "Asthma / COPD"},
    "budesonide": {"generic": "Budesonide", "purpose": "Asthma inhaler / Steroid"},
    "montelukast": {"generic": "Montelukast", "purpose": "Asthma / Allergy"},
    "levocetirizine": {"generic": "Levocetirizine", "purpose": "Allergy"},
    "cetirizine": {"generic": "Cetirizine", "purpose": "Allergy"},
    "loratadine": {"generic": "Loratadine", "purpose": "Allergy"},

    # --- Anticoagulants / Blood thinners ---
    "warfarin": {"generic": "Warfarin", "purpose": "Anticoagulant"},
    "heparin": {"generic": "Heparin", "purpose": "Anticoagulant (Injection)"},
    "enoxaparin": {"generic": "Enoxaparin", "purpose": "Anticoagulant (Injection)"},
    "dabigatran": {"generic": "Dabigatran", "purpose": "Oral anticoagulant"},
    "apixaban": {"generic": "Apixaban", "purpose": "Oral anticoagulant"},
    "rivaroxaban": {"generic": "Rivaroxaban", "purpose": "Oral anticoagulant"},
    "clopidogrel": {"generic": "Clopidogrel", "purpose": "Antiplatelet"},
    "ecosprin": {"generic": "Aspirin", "purpose": "Antiplatelet / Heart protection"},

    # --- ICU / Emergency ---
    "adrenaline": {"generic": "Epinephrine", "purpose": "Anaphylaxis / CPR"},
    "noradrenaline": {"generic": "Norepinephrine", "purpose": "Shock"},
    "dopamine": {"generic": "Dopamine", "purpose": "Shock / Heart failure"},
    "dobutamine": {"generic": "Dobutamine", "purpose": "Heart failure"},
    "propofol": {"generic": "Propofol", "purpose": "Anesthesia"},
    "midazolam": {"generic": "Midazolam", "purpose": "Sedation / ICU"},
    "fentanyl": {"generic": "Fentanyl", "purpose": "Strong painkiller"},
    "morphine": {"generic": "Morphine", "purpose": "Severe pain / Cancer pain"},
    "naloxone": {"generic": "Naloxone", "purpose": "Opioid antidote"},
    # --- Men's Health ---
    "sildenafil": {"generic": "Sildenafil", "purpose": "Erectile dysfunction"},
    "tadalafil": {"generic": "Tadalafil", "purpose": "Erectile dysfunction / BPH"},
    "vardenafil": {"generic": "Vardenafil", "purpose": "Erectile dysfunction"},
    "avanafil": {"generic": "Avanafil", "purpose": "Erectile dysfunction"},
    "dutasteride": {"generic": "Dutasteride", "purpose": "Prostate enlargement"},
    "finasteride": {"generic": "Finasteride", "purpose": "Prostate / Hair loss"},
    "tamsulosin": {"generic": "Tamsulosin", "purpose": "Prostate enlargement (BPH)"},
    "alfuzosin": {"generic": "Alfuzosin", "purpose": "Prostate enlargement (BPH)"},
    "silodosin": {"generic": "Silodosin", "purpose": "BPH"},
    "clomiphene": {"generic": "Clomiphene citrate", "purpose": "Male infertility (off-label)"},

    # --- Women's Health (Gynaecology / Fertility) ---
    "clomiphene citrate": {"generic": "Clomiphene citrate", "purpose": "Female infertility / Ovulation induction"},
    "letrozole": {"generic": "Letrozole", "purpose": "Ovulation induction / Breast cancer"},
    "gonadotropin": {"generic": "hMG / FSH", "purpose": "Infertility treatment"},
    "cabergoline": {"generic": "Cabergoline", "purpose": "High prolactin / Infertility"},
    "bromocriptine": {"generic": "Bromocriptine", "purpose": "High prolactin"},
    "metformin (pcos)": {"generic": "Metformin", "purpose": "PCOS management"},
    "dydrogesterone": {"generic": "Dydrogesterone", "purpose": "Luteal phase support / Miscarriage"},
    "progesterone": {"generic": "Progesterone", "purpose": "Pregnancy support"},
    "estradiol": {"generic": "Estradiol", "purpose": "Hormone replacement / Infertility"},
    "norethisterone": {"generic": "Norethisterone", "purpose": "Period regulation"},
    "medroxyprogesterone": {"generic": "Medroxyprogesterone", "purpose": "Period disorders / Contraception"},
    "levonorgestrel": {"generic": "Levonorgestrel", "purpose": "Emergency contraception"},
    "ulipristal": {"generic": "Ulipristal acetate", "purpose": "Emergency contraception"},
    "desogestrel": {"generic": "Desogestrel", "purpose": "Contraceptive pill"},
    "drospirenone": {"generic": "Drospirenone", "purpose": "Oral contraceptive"},
    "ethinylestradiol": {"generic": "Ethinylestradiol", "purpose": "Oral contraceptive"},

    # --- Pregnancy & Lactation ---
    "folic acid": {"generic": "Folic Acid", "purpose": "Pregnancy supplement"},
    "iron folate": {"generic": "Iron + Folic Acid", "purpose": "Anemia in pregnancy"},
    "calcium carbonate": {"generic": "Calcium Carbonate", "purpose": "Bone health in pregnancy"},
    "vitamin d3": {"generic": "Cholecalciferol", "purpose": "Supplement in pregnancy"},
    "dha supplement": {"generic": "Docosahexaenoic Acid", "purpose": "Brain development in pregnancy"},
    "aspirin low dose": {"generic": "Low-dose Aspirin", "purpose": "Prevent preeclampsia in pregnancy"},

    # --- UTI & Vaginal Health ---
    "nitrofurantoin": {"generic": "Nitrofurantoin", "purpose": "UTI"},
    "fosfomycin": {"generic": "Fosfomycin", "purpose": "UTI"},
    "fluconazole vaginal": {"generic": "Fluconazole", "purpose": "Vaginal yeast infection"},
    "clotrimazole vaginal": {"generic": "Clotrimazole", "purpose": "Vaginal antifungal"},
    "metronidazole": {"generic": "Metronidazole", "purpose": "Bacterial vaginosis / Trichomoniasis"},
    "tinidazole": {"generic": "Tinidazole", "purpose": "Vaginal infection"},
    "boric acid suppository": {"generic": "Boric Acid", "purpose": "Recurrent vaginal infection"},

    # --- Menopause / HRT ---
    "conjugated estrogens": {"generic": "Estrogens", "purpose": "Hormone replacement"},
    "raloxifene": {"generic": "Raloxifene", "purpose": "Osteoporosis in women"},
    "bisphosphonates": {"generic": "Alendronate / Risedronate", "purpose": "Osteoporosis"},

    # --- Sexual Health / STI ---
    "acyclovir": {"generic": "Acyclovir", "purpose": "Herpes simplex / Genital herpes"},
    "valacyclovir": {"generic": "Valacyclovir", "purpose": "Herpes management"},
    "doxycycline": {"generic": "Doxycycline", "purpose": "STI / Chlamydia"},
    "azithromycin sti": {"generic": "Azithromycin", "purpose": "STI (Chlamydia / Gonorrhea)"},

}

TEST_KEYWORDS = {
    # --- Neurology / Neurophysiology ---
    "EEG", "EMG", "NCV", "VEP", "BERA", "NCS", "Sleep Study",
    
    # --- Imaging / Radiology ---
    "MRI", "CT", "PET-CT", "X-Ray", "Ultrasound", "USG",
    "Sonography", "Mammography", "Doppler", "Echocardiogram",
    "Echo", "Fluoroscopy", "Angiography", "MRCP", "HSG",
    "DEXA", "Bone Scan",

    # --- Blood Tests (General Pathology) ---
    "CBC", "Complete Blood Count", "Hemogram",
    "ESR", "CRP", "LDH", "Procalcitonin",
    "Blood Sugar", "Fasting Blood Sugar", "Postprandial Sugar",
    "HbA1c", "Blood Group", "Cross Match",
    "Reticulocyte Count", "Coombs Test", "D-Dimer",

    # --- Biochemistry / Organ Function ---
    "LFT", "Liver Function Test", "KFT", "RFT", "Renal Function Test",
    "Electrolytes", "Calcium", "Phosphorus", "Uric Acid",
    "Amylase", "Lipase", "CPK", "CK-MB", "Troponin",

    # --- Lipid / Heart Profile ---
    "Lipid Profile", "Cholesterol", "HDL", "LDL", "Triglycerides",
    "Apolipoprotein", "BNP", "NT-proBNP", "ECG", "TMT", "Holter",

    # --- Endocrine / Hormonal ---
    "Thyroid Profile", "TSH", "T3", "T4", "Free T4", "Anti-TPO",
    "Cortisol", "ACTH", "Insulin", "C-Peptide", "Prolactin",
    "LH", "FSH", "Estradiol", "Progesterone", "Testosterone",
    "AMH", "DHEAS", "Growth Hormone",

    # --- Infection / Serology ---
    "HIV Test", "HIV ELISA", "HCV Test", "HBsAg",
    "Hepatitis Panel", "VDRL", "RPR", "TPHA",
    "Widal Test", "Typhidot", "Dengue NS1", "Dengue IgM",
    "Malaria Smear", "Rapid Malaria Test", "TB Gold",
    "Mantoux", "COVID-19 RT-PCR", "COVID-19 Antigen",
    "Influenza A/B", "H1N1 PCR",

    # --- Urine / Stool ---
    "Urine Routine", "Urine Culture", "24H Urine Protein",
    "Stool Routine", "Stool Occult Blood", "Stool Culture",
    "Stool Ova Cyst", "Stool H. Pylori Antigen",

    # --- Cancer / Tumor Markers ---
    "PSA", "CEA", "CA-125", "CA-19.9", "CA-15.3",
    "AFP", "Beta-HCG", "LDH", "NSE", "BRCA1", "BRCA2",

    # --- Hematology / Clotting ---
    "PT", "INR", "aPTT", "Fibrinogen", "Platelet Count",
    "Bleeding Time", "Clotting Time", "Thrombophilia Panel",

    # --- Microbiology / Cultures ---
    "Blood Culture", "Urine Culture", "Sputum Culture",
    "Throat Swab", "CSF Culture", "Wound Culture",
    "Gram Stain", "AFB Stain", "KOH Mount",

    # --- Prenatal / Fertility / Women’s Health ---
    "NT Scan", "Anomaly Scan", "NIPT", "Double Marker",
    "Triple Marker", "Quadruple Marker",
    "TORCH Panel", "Pregnancy Test", "Urine hCG",
    "Beta-hCG Quantitative", "AMH", "Follicular Study",

    # --- Genetic / Advanced ---
    "Karyotyping", "PCR", "FISH", "NGS",
    "Whole Genome Sequencing", "HLA Typing",
    "Bone Marrow Biopsy", "CSF Analysis",
     # --- Advanced Radiology / Special Scans ---
    "HRCT", "PET Scan", "SPECT", "Angio CT", "Coronary Angiography",
    "CT Angiography", "MR Angiography", "Functional MRI", "Diffusion MRI",
    "Spine MRI", "Brain MRI", "Chest CT", "Abdominal CT",

    # --- Cardiology (missed earlier) ---
    "2D Echo", "3D Echo", "Stress Echo", "Cardiac MRI",
    "Electrophysiology Study", "Coronary Calcium Score",
    "ABPM", "BP Monitoring", "Cardiac Enzymes",

    # --- Pulmonology / Chest ---
    "PFT", "Pulmonary Function Test", "Spirometry",
    "Bronchoscopy", "BAL Fluid Analysis", "Chest X-Ray",
    "DLCO", "Sleep Apnea Test",

    # --- Gastroenterology ---
    "Endoscopy", "Colonoscopy", "Sigmoidoscopy",
    "ERCP", "Liver Biopsy", "FibroScan", "Stool Calprotectin",
    "Fecal Elastase",

    # --- Nephrology / Kidney ---
    "Urine Protein", "Microalbuminuria", "Creatinine Clearance",
    "Kidney Biopsy", "Dialysis Adequacy Test", "eGFR",

    # --- Orthopedics / Bone ---
    "X-Ray Hip", "X-Ray Knee", "X-Ray Spine",
    "Bone Density", "DEXA Scan", "Vitamin D Level",
    "Serum Calcium", "Alkaline Phosphatase (Bone)",

    # --- Ophthalmology (Eye) ---
    "Fundus Photography", "OCT", "Visual Field Test",
    "Tonometry", "Slit Lamp", "Corneal Topography",
    "Fluorescein Angiography", "ERG",

    # --- ENT (Ear Nose Throat) ---
    "Audiometry", "Pure Tone Audiogram", "Impedance Audiometry",
    "Tympanometry", "Laryngoscopy", "Sinus CT", "Nasal Endoscopy",

    # --- Dermatology / Allergy ---
    "Skin Biopsy", "Patch Test", "Prick Test",
    "Allergy Panel", "IgE", "ANA", "Anti-dsDNA",

    # --- Rheumatology / Autoimmune ---
    "RA Factor", "Anti-CCP", "HLA-B27", "ANCA", "CRYOglobulin",
    "Complement C3", "Complement C4",

    # --- Oncology (missed earlier tumor tests) ---
    "CA-72.4", "CA-27.29", "CYFRA 21-1", "SCC Antigen",
    "BCR-ABL", "JAK2 Mutation", "ALK Mutation",
    "EGFR Mutation", "PD-L1",

    # --- Infectious Disease (missed ones) ---
    "Leptospira IgM", "Scrub Typhus IgM", "Brucella Antibody",
    "Toxoplasma IgG", "Toxoplasma IgM",
    "Rubella IgG", "Rubella IgM",

    # --- Prenatal / Pregnancy (extra) ---
    "NT Scan", "Level II Scan", "Anomaly Ultrasound",
    "Fetal Echo", "Cord Blood Doppler", "Placental Doppler",
    "Kleihauer-Betke Test",

    # --- ICU / Emergency (extra) ---
    "ABG", "Arterial Blood Gas", "Serum Lactate",
    "Base Excess", "Osmolality", "Toxicology Screen",
    "Drug Level Monitoring", "Therapeutic Drug Monitoring",

    # --- Miscellaneous / Screening ---
    "Pap Smear", "HPV DNA Test", "PSG", "Hearing Screening",
    "Newborn Screening", "Blood Spot Test", "G6PD",
    "Vitamin B12", "Folate Level", "Zinc Level",
    "Copper Level", "Lead Level", "Heavy Metal Panel",
}

SPECIALIST_RULES = [
    # --- Basic / General ---
    (r'\bfever|cold|cough|flu|viral|infection|weakness|body ache|general illness|malaise\b',
    ["General Physician", "Internal Medicine Specialist"]),
    (r'\bwound|cut|abscess|boil|laceration|appendicitis minor|general surgery\b',
    ["General Surgeon"]),
    (r'\bpreventive|family checkup|annual checkup|routine health|lifestyle disease\b',
    ["Family Medicine Specialist"]),
    (r'\bvaccination drive|immunization|epidemic|outbreak|public health|screening camp\b',
    ["Community Medicine Specialist", "Public Health Expert"]),
    # --- Oncology / Cancer ---
    (r'\bcarcinoma|cancer|tumou?r|metastases?|lymphoma|leukemia|sarcoma|myeloma\b', ["Oncologist", "Hematologist"]),

    # --- Neurology / Neurosurgery ---
    (r'\bseizure|epilep|stroke|parkinson|alzheim|multiple sclerosis|migraine|neuropathy|brain tumor|meningioma\b', ["Neurologist"]),
    (r'\bhead injury|intracranial bleed|aneurysm|brain surgery|spine surgery\b', ["Neurosurgeon"]),

    # --- Cardiology / Cardiac Surgery ---
    (r'\bheart attack|myocardial infarction|angina|arrhythmia|cardiomyopathy|ecg abnormal|hypertension|coronary\b', ["Cardiologist"]),
    (r'\bvalve replacement|bypass surgery|cabg|open heart surgery\b', ["Cardiac Surgeon"]),

    # --- Pulmonology / Respiratory Medicine ---
    (r'\basthma|copd|bronchitis|pneumonia|lung fibrosis|tuberculosis|tb|breathlessness|sleep apnea\b', ["Pulmonologist", "Chest Specialist"]),
    (r'\bthoracic surgery|lung resection|lobectomy\b', ["Thoracic Surgeon"]),

    # --- Gastroenterology / Hepatology ---
    (r'\bgastritis|ulcer|hepatitis|jaundice|cirrhosis|fatty liver|ibs|colitis|pancreatitis|crohn|celiac\b', ["Gastroenterologist", "Hepatologist"]),
    (r'\bliver transplant|hepatic failure\b', ["Hepatologist", "Transplant Surgeon"]),

    # --- Nephrology / Urology ---
    (r'\bkidney|renal failure|ckd|dialysis|proteinuria|hematuria|nephritis\b', ["Nephrologist"]),
    (r'\bprostate|bph|erectile dysfunction|urinary retention|stones|urolithiasis|uti\b', ["Urologist"]),

    # --- Endocrinology / Diabetes ---
    (r'\bdiabetes|thyroid|hypothyroid|hyperthyroid|pcos|adrenal|pituitary|cortisol|hormonal\b', ["Endocrinologist"]),

    # --- Rheumatology / Autoimmune ---
    (r'\barthritis|rheumatism|sle|lupus|scleroderma|vasculitis|gout|ankylosing\b', ["Rheumatologist"]),

    # --- Dermatology / Skin / Venereology ---
    (r'\bskin rash|eczema|psoriasis|fungal infection|alopecia|acne|urticaria|venereal disease|std|sti\b', ["Dermatologist", "Venereologist"]),

    # --- Psychiatry / Psychology ---
    (r'\bdepression|anxiety|bipolar|schizophrenia|adhd|insomnia|suicidal|mental health\b', ["Psychiatrist"]),
    (r'\bcounseling|therapy|stress management|behavioral issue\b', ["Psychologist"]),

    # --- ENT (Ear, Nose, Throat) ---
    (r'\bpharyngeal|tonsillitis|sinusitis|otitis|ear infection|hearing loss|vertigo|nasal polyp|laryngitis\b', ["ENT Specialist"]),

    # --- Ophthalmology (Eye) ---
    (r'\bglaucoma|cataract|retinopathy|vision loss|eye pain|conjunctivitis|corneal ulcer|squint\b', ["Ophthalmologist"]),

    # --- Orthopedics / Trauma ---
    (r'\bfracture|arthritis|osteoporosis|joint pain|back pain|disc prolapse|ligament injury|scoliosis\b', ["Orthopedic Surgeon"]),
    (r'\bsports injury|arthroscopy|acl tear|meniscus\b', ["Sports Medicine Specialist"]),

    # --- Gynecology / Obstetrics (Women’s Health) ---
    (r'\bmenstruation|period pain|pcos|fibroid|endometriosis|miscarriage|infertility|contraception\b', ["Gynecologist"]),
    (r'\blabour pain|pregnancy|cesarean|antenatal|postnatal\b', ["Obstetrician"]),

    # --- Pediatrics / Neonatology ---
    (r'\bchild|infant|newborn|pediatric|growth delay|vaccination|neonatal\b', ["Pediatrician", "Neonatologist"]),

    # --- Geriatrics (Elderly) ---
    (r'\belderly|dementia|falls elderly|osteoporosis elderly|geriatric care\b', ["Geriatric Specialist"]),

    # --- Hematology / Blood Disorders ---
    (r'\banemia|thalassemia|hemophilia|clotting disorder|polycythemia|aplastic anemia\b', ["Hematologist"]),

    # --- Infectious Disease / Tropical Medicine ---
    (r'\bhiv|aids|malaria|dengue|typhoid|covid|swine flu|hepatitis infectious|zika|chikungunya\b', ["Infectious Disease Specialist"]),

    # --- Dentistry / Oral Health ---
    (r'\btoothache|dental|cavity|periodontitis|gum disease|root canal|oral cancer|orthodontic\b', ["Dentist"]),

    # --- Surgery / Super-Specialties ---
    (r'\bappendicitis|hernia|gallstone|piles|fistula|abscess|laparoscopic surgery\b', ["General Surgeon"]),
    (r'\bvascular surgery|aortic aneurysm|varicose veins\b', ["Vascular Surgeon"]),
    (r'\bknee replacement|hip replacement|spinal fixation\b', ["Orthopedic Surgeon"]),
    (r'\bplastic surgery|burn scar|cosmetic|cleft lip\b', ["Plastic Surgeon"]),
    (r'\btransplant\b', ["Transplant Surgeon"]),

    # --- Critical Care / ICU / Emergency ---
    (r'\bshock|ventilator|multi organ failure|sepsis|icu required|critical care\b', ["Critical Care Specialist"]),

    # --- Immunology / Allergy ---
    (r'\ballergy|hay fever|immune deficiency|anaphylaxis|asthma allergic\b', ["Immunologist", "Allergist"]),

    # --- Nutrition / Dietetics ---
    (r'\bobesity|weight loss|malnutrition|vitamin deficiency|diet plan|nutritional\b', ["Dietitian / Nutritionist"]),

    # --- Physiotherapy / Rehabilitation ---
    (r'\bparalysis|rehab|physiotherapy|stroke recovery|post-surgery rehab\b', ["Physiotherapist"]),

    # --- Occupational Therapy / Speech Therapy ---
    (r'\bspeech delay|stammering|voice disorder|autism therapy|ot therapy\b', ["Speech Therapist", "Occupational Therapist"]),

    # --- Alternative Medicine (common in India) ---
    (r'\bayurveda|homeopathy|unani|naturopathy\b', ["Alternative Medicine Specialist"]),
    
    # --- Oncology / Cancer ---
    (r'\bcarcinoma|cancer|metastases?|tumou?r|lymphoma|leukemia|sarcoma\b', ["Oncologist"]),
    
    # --- Neurology ---
    (r'\bseizure|epilep|stroke|parkinson|alzheim|multiple sclerosis|migraine|headache|neuropathy\b', ["Neurologist"]),
    
    # --- Cardiology ---
    (r'\bheart attack|myocardial infarction|angina|arrhythmia|cardiomyopathy|ecg abnormal|hypertension|coronary\b', ["Cardiologist"]),
    
    # --- Pulmonology (Chest / Lung) ---
    (r'\basthma|copd|bronchitis|pneumonia|lung fibrosis|tb|tuberculosis|breathlessness\b', ["Pulmonologist"]),
    
    # --- Gastroenterology ---
    (r'\bgastritis|ulcer|hepatitis|jaundice|cirrhosis|fatty liver|ibs|colitis|pancreatitis\b', ["Gastroenterologist"]),
    
    # --- Nephrology (Kidney) ---
    (r'\bkidney|renal failure|ckd|proteinuria|hematuria|nephritis\b', ["Nephrologist"]),
    
    # --- Endocrinology ---
    (r'\bdiabetes|thyroid|hypothyroidism|hyperthyroidism|pcos|adrenal|cortisol|hormonal\b', ["Endocrinologist"]),
    
    # --- Rheumatology / Autoimmune ---
    (r'\barthritis|rheumatism|sle|lupus|scleroderma|vasculitis|gout|autoimmune\b', ["Rheumatologist"]),
    
    # --- Dermatology / Skin ---
    (r'\bskin rash|eczema|psoriasis|dermatitis|fungal infection|alopecia|acne|urticaria\b', ["Dermatologist"]),
    
    # --- Psychiatry / Mental Health ---
    (r'\bdepression|anxiety|bipolar|schizophrenia|adhd|insomnia|mental health|suicidal\b', ["Psychiatrist"]),
    
    # --- ENT (Ear, Nose, Throat) ---
    (r'\bpharyngeal|throat|tonsillitis|sinusitis|otitis|ear infection|hearing loss|vertigo\b', ["ENT Specialist"]),
    
    # --- Ophthalmology (Eye) ---
    (r'\bglaucoma|cataract|retinopathy|vision loss|eye pain|diabetic eye|conjunctivitis\b', ["Ophthalmologist"]),
    
    # --- Orthopedics / Bones ---
    (r'\bfracture|arthritis|osteoporosis|joint pain|back pain|disc prolapse|spine injury\b', ["Orthopedic Surgeon"]),
    
    # --- Urology (Urinary / Male health) ---
    (r'\bbph|prostate|erectile dysfunction|urinary retention|stones|urolithiasis|hematuria\b', ["Urologist"]),
    
    # --- Gynecology / Women’s Health ---
    (r'\bmenstruation|pregnancy|pcos|fibroid|endometriosis|miscarriage|infertility\b', ["Gynecologist"]),
    
    # --- Pediatrics (Children) ---
    (r'\bchild|infant|newborn|pediatric|growth delay|vaccination\b', ["Pediatrician"]),
    
    # --- Geriatrics (Elderly Care) ---
    (r'\belderly|memory loss|falls in elderly|osteoporosis elderly\b', ["Geriatric Specialist"]),
    
    # --- Hematology (Blood Disorders) ---
    (r'\banemia|thalassemia|hemophilia|clotting disorder|blood disorder\b', ["Hematologist"]),
    
    # --- Infectious Disease ---
    (r'\bhiv|aids|malaria|dengue|typhoid|covid|swine flu|hepatitis infectious\b', ["Infectious Disease Specialist"]),
    
    # --- Dentistry ---
    (r'\btoothache|dental|cavity|periodontitis|gum disease|oral cancer\b', ["Dentist"]),
    
    # --- Surgery / General Surgery ---
    (r'\bappendicitis|hernia|gallstone|piles|fistula|abscess|surgery required\b', ["General Surgeon"]),
    
    # --- Plastic / Reconstructive Surgery ---
    (r'\bplastic surgery|cosmetic|burn scar|cleft lip\b', ["Plastic Surgeon"]),
    
    # --- Obstetrics (Pregnancy Delivery) ---
    (r'\blabour pain|normal delivery|cesarean|antenatal\b', ["Obstetrician"]),
    
    # --- Critical Care / ICU ---
    (r'\bshock|ventilator|multi organ failure|sepsis|icu required\b', ["Critical Care Specialist"]),
    
    # --- Immunology / Allergy ---
    (r'\ballergy|asthma allergic|hay fever|immune deficiency\b', ["Immunologist"]),
    
    # --- Nutrition / Dietetics ---
    (r'\bobesity|weight loss|malnutrition|vitamin deficiency|diet plan\b', ["Dietitian / Nutritionist"]),
]

RECO_RULES = {
    # --- General ---
    "general": [
        "Keep all prescriptions & reports together",
        "Maintain a healthy diet & hydration",
        "Report any new or worsening symptoms immediately"
    ],

    # --- Fever & Infections ---
    "fever": [
        "Stay hydrated and monitor temperature regularly",
        "Take prescribed antipyretics if needed",
        "Consult a doctor if fever persists beyond 3 days"
    ],
    "infection": [
        "Complete the full antibiotic course if prescribed",
        "Maintain proper hygiene to prevent spread",
        "Seek medical attention if symptoms worsen"
    ],
    "covid": [
        "Isolate and follow COVID protocols",
        "Monitor oxygen saturation regularly",
        "Seek hospital care if breathlessness worsens"
    ],
    "dengue": [
        "Monitor platelet counts regularly",
        "Stay hydrated with fluids",
        "Avoid painkillers like ibuprofen/aspirin"
    ],
    "malaria": [
        "Complete the full anti-malarial course",
        "Use mosquito nets/repellents",
        "Seek urgent care if fever spikes return"
    ],
    "typhoid": [
        "Adhere to full antibiotic treatment",
        "Eat light, soft diet",
        "Do follow-up blood tests after treatment"
    ],
    "tuberculosis": [
        "Strictly adhere to the full anti-TB course",
        "Isolate if infectious to prevent spread",
        "Monitor for drug side effects"
    ],

    # --- Respiratory ---
    "asthma": [
        "Always carry and use inhalers as prescribed",
        "Avoid dust, smoke, and known allergens",
        "Schedule regular follow-ups with a pulmonologist"
    ],
    "copd": [
        "Quit smoking immediately",
        "Use prescribed bronchodilators and oxygen support",
        "Join pulmonary rehabilitation programs"
    ],
    "pneumonia": [
        "Complete the antibiotic/antiviral course",
        "Take plenty of rest and fluids",
        "Seek urgent care if breathing difficulty increases"
    ],

    # --- Cardiac ---
    "hypertension": [
        "Monitor blood pressure regularly",
        "Reduce salt intake and manage stress",
        "Take antihypertensive medicines consistently"
    ],
    "heart attack": [
        "Seek emergency care immediately",
        "Take prescribed antiplatelets/anticoagulants",
        "Adopt a heart-healthy lifestyle after recovery"
    ],
    "arrhythmia": [
        "Take medications consistently",
        "Avoid excess caffeine and alcohol",
        "Do regular ECG check-ups"
    ],
    "heart failure": [
        "Limit salt and fluid intake",
        "Monitor weight daily for fluid retention",
        "Take prescribed diuretics & heart medications"
    ],

    # --- Endocrine & Metabolic ---
    "diabetes": [
        "Monitor blood sugar regularly",
        "Follow strict diet & exercise routine",
        "Take antidiabetic medication/insulin as prescribed"
    ],
    "thyroid": [
        "Take thyroid medication daily at the same time",
        "Check thyroid function tests periodically",
        "Report unexplained weight or mood changes"
    ],
    "obesity": [
        "Adopt a calorie-controlled diet plan",
        "Exercise at least 30 minutes daily",
        "Seek medical/dietician advice for long-term plan"
    ],
    "pcos": [
        "Maintain healthy weight & diet",
        "Take hormonal treatment as prescribed",
        "Regular gynecology follow-up is essential"
    ],

    # --- Neurology ---
    "seizure": [
        "Do not skip anti-seizure medicines",
        "Avoid driving/heights until cleared",
        "Neurology follow-up for dose adjustment"
    ],
    "stroke": [
        "Seek emergency medical help immediately",
        "Begin physiotherapy/rehab early",
        "Control BP, sugar, and cholesterol strictly"
    ],
    "migraine": [
        "Identify and avoid known triggers",
        "Take prescribed medicine at first sign",
        "Maintain sleep & stress management"
    ],
    "parkinson": [
        "Adhere to Parkinson’s medications strictly",
        "Do regular physiotherapy/exercises",
        "Regular neurology follow-up for dose titration"
    ],
    "dementia": [
        "Create a safe environment to prevent accidents",
        "Maintain a daily routine",
        "Caregiver support & counseling is vital"
    ],

    # --- Oncology ---
    "cancer": [
        "Consult an oncologist urgently",
        "Follow staging workup (PET-CT / MRI) as advised",
        "Consider nutrition & palliative care if advanced"
    ],
    "leukemia": [
        "Seek immediate hematology/oncology care",
        "Regular blood counts and bone marrow follow-up",
        "Avoid infections; practice strict hygiene"
    ],

    # --- Gastro & Liver ---
    "gastritis": [
        "Avoid spicy/oily foods",
        "Take PPIs/antacids as prescribed",
        "Limit alcohol, caffeine, smoking"
    ],
    "ulcer": [
        "Take H. pylori treatment if advised",
        "Avoid NSAIDs (painkillers like ibuprofen)",
        "Regular endoscopy if recurrent"
    ],
    "liver disease": [
        "Avoid alcohol completely",
        "Take prescribed liver-protective medicines",
        "Regularly monitor liver function tests"
    ],
    "hepatitis": [
        "Avoid sharing needles or razors",
        "Take antiviral therapy if advised",
        "Monitor liver health regularly"
    ],
    "pancreatitis": [
        "Avoid alcohol and fatty food strictly",
        "Hospital admission may be required",
        "Follow low-fat diet after recovery"
    ],

    # --- Renal / Nephrology ---
    "ckd": [
        "Regular kidney function monitoring",
        "Control BP & diabetes strictly",
        "Restrict salt/protein as advised"
    ],
    "kidney stone": [
        "Drink 3-4 liters of water daily",
        "Take pain relief/stone dissolvers as prescribed",
        "Seek surgery if stones persist"
    ],
    "uti": [
        "Drink plenty of fluids",
        "Complete antibiotic course",
        "Maintain proper personal hygiene"
    ],

    # --- Women’s Health / Pregnancy ---
    "pregnancy": [
        "Attend regular antenatal checkups",
        "Take iron/folic acid supplements",
        "Avoid smoking, alcohol, and harmful drugs"
    ],
    "menopause": [
        "Consult doctor for HRT if needed",
        "Maintain calcium & vitamin D intake",
        "Exercise regularly to prevent osteoporosis"
    ],

    # --- Pediatrics ---
    "child vaccination": [
        "Follow the national immunization schedule",
        "Do not delay booster doses",
        "Keep vaccination card updated"
    ],
    "malnutrition": [
        "Provide balanced diet with proteins & vitamins",
        "Give iron, calcium, vitamin supplements if prescribed",
        "Regular pediatric follow-up for growth monitoring"
    ],

    # --- Skin / Dermatology ---
    "psoriasis": [
        "Use prescribed topical/systemic therapy",
        "Avoid triggers like stress & skin injury",
        "Moisturize skin daily"
    ],
    "eczema": [
        "Avoid scratching & allergens",
        "Use emollients regularly",
        "Take antihistamines/topical steroids as prescribed"
    ],
    "fungal infection": [
        "Keep affected area clean & dry",
        "Use antifungal creams as prescribed",
        "Avoid sharing clothes/towels"
    ],

    # --- Psychiatry / Mental Health ---
    "depression": [
        "Do not stop antidepressants suddenly",
        "Seek regular counseling/therapy",
        "Maintain social support & routine"
    ],
    "anxiety": [
        "Practice relaxation techniques daily",
        "Avoid stimulants like caffeine",
        "Consult psychiatrist if severe"
    ],
    "schizophrenia": [
        "Adhere to antipsychotic medication strictly",
        "Ensure regular psychiatric follow-ups",
        "Family support & therapy is crucial"
    ],
}

def _fuzzy_pick(name: str, vocab: dict, score_cutoff=85):
    name_l = name.lower()
    best = process.extractOne(name_l, list(vocab.keys()), scorer=fuzz.token_sort_ratio, score_cutoff=score_cutoff)
    if best and len(best) >= 1:
        return best[0]
    return None


def group_entities(entities):
    grouped = {
        "patient_info": set(),
        "conditions": set(),
        "medications": [],
        "tests": set(),
        "timeline": set()
    }

    for ent in entities:
        cat = ent.get("Type", "").upper()
        txt = ent.get("Text", "").strip()
        if not txt:
            continue

        # ✅ Apply OCR + fuzzy corrections here
        clean_txt = auto_correct(txt)

        if cat in ("PROTECTED_HEALTH_INFORMATION",):
            grouped["patient_info"].add(clean_txt)
        elif cat in ("MEDICAL_CONDITION",):
            grouped["conditions"].add(clean_txt)
        elif cat in ("MEDICATION",):
            grouped["medications"].append(clean_txt)
        elif cat in ("TEST_TREATMENT_PROCEDURE",):
            grouped["tests"].add(clean_txt)
        elif cat in ("TIME_EXPRESSION",):
            grouped["timeline"].add(clean_txt)

    # --- normalize medications to canonical (brand→generic + purpose) ---
    meds_struct = []
    for m in grouped["medications"]:
        dose = re.search(r'(\d+\s*(?:mg|mcg|ml))', m, flags=re.I)
        base = re.sub(r'(\d+\s*(?:mg|mcg|ml))', '', m, flags=re.I).strip()

        base_low = auto_correct(base).lower()
        key = _fuzzy_pick(base_low, MEDICATION_CANON) or base_low
        info = MEDICATION_CANON.get(key, {"generic": "", "purpose": ""})

        meds_struct.append({
            "name": m,
            "canonical": key.title(),
            "generic": info.get("generic", ""),
            "purpose": info.get("purpose", ""),
            "dose": dose.group(1) if dose else ""
        })
    grouped["medications"] = meds_struct

    # --- normalize tests by keyword hit + deduplicate ---
    tests_norm = set()
    for t in list(grouped["tests"]):
        clean_t = auto_correct(t)
        hit = _fuzzy_pick(clean_t, {k.lower(): None for k in TEST_KEYWORDS}, score_cutoff=80)
        norm = hit.upper() if hit else clean_t.upper()
        tests_norm.add(norm)
    grouped["tests"] = sorted(tests_norm)

    # --- normalize conditions ---
    conds_norm = []
    for c in grouped["conditions"]:
        conds_norm.append(auto_correct(c))
    grouped["conditions"] = sorted(set(conds_norm))

    # final cleanup
    grouped["patient_info"] = sorted(grouped["patient_info"])
    grouped["timeline"] = sorted(grouped["timeline"])
    return grouped

def analyze_medical_text(text, access_key, secret_key, region='us-east-1'):
    client = boto3.client(
        'comprehendmedical',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )

    response = client.detect_entities_v2(Text=text)
    entities = response['Entities']

    return [{'Text': ent['Text'], 'Type': ent['Category']} for ent in entities]
# --- extend in text_analyzer.py ---
def _pull_field(pattern, text, flags=re.I):
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else ""

def infer_specialists(text, grouped):
    specs = set()
    blob = (text + " " + " ".join(grouped.get("conditions",[]))).lower()
    for pat, spec_list in SPECIALIST_RULES:
        if re.search(pat, blob):
            specs.update(spec_list)
    return sorted(specs) or ["General Physician"]

def make_recommendations(grouped):
    recs = set(RECO_RULES["general"])
    blob = " ".join(grouped.get("conditions", []) + [m["canonical"] for m in grouped.get("medications",[])])
    if re.search(r'carcinoma|cancer|metastases', blob, flags=re.I):
        recs.update(RECO_RULES["cancer"])
    if re.search(r'seizure|levipil|levetiracetam', blob, flags=re.I):
        recs.update(RECO_RULES["seizure"])
    return sorted(recs)


def build_summary(clean_text: str, entities):
    grouped = group_entities(entities)

    # ✅ Patient name fix
    patient = _pull_field(r'(Mr\.|Mrs\.|Ms\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', clean_text)
    if not patient:
        patient = _pull_field(r'Name[:\-]?\s*([A-Za-z ]{3,})', clean_text)

    age_gender = _pull_field(r'\b(\d{1,2}\s*[/\-]?\s*[MFmf])\b', clean_text)
    date = _pull_field(r'\b(\d{1,2}\s+\w+\s+20\d{2}|\d{1,2}[-/]\w+[-/]\d{2,4})\b', clean_text)
    doctor = _pull_field(r'(Dr\.\s*[A-Z][A-Za-z. ]+)', clean_text)
    hospital = _pull_field(r'([A-Z][A-Z ]{8,}NEUROLOGY[^\n]*)', clean_text)

    specialists = infer_specialists(clean_text, grouped)
    recommendations = make_recommendations(grouped)

    summary = {
        "Patient Information": {
            "Name": patient or "",
            "Age/Gender": age_gender or "",
            "Doctor": doctor or "",
            "Hospital/Clinic": hospital or "",
            "Date": date or ""
        },
        "Medical Conditions": grouped["conditions"],
        "Medications": grouped["medications"],
        "Tests / Procedures": grouped["tests"],
        "Suggested Specialists": specialists,
        "Recommendations": recommendations
    }
    return summary
