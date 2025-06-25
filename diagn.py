# ICD-10 Mapping for common conditions
icd10_map = {
    "hypertension": "I10",
    "diabetes": "E11", 
    "type 1 diabetes": "E10",
    "type 2 diabetes": "E11",
    "asthma": "J45",
    "cancer": "C80.1",  # Malignant neoplasm, unspecified
    "covid-19": "U07.1",
    "tuberculosis": "A15",
    "arthritis": "M19.90",
    "hepatitis": "B19.9",
    "anemia": "D64.9",
    "malaria": "B50.9",
    "migraine": "G43.9",
    "depression": "F32.9",
    "anxiety": "F41.9",
    "obesity": "E66.9",
    "eczema": "L30.9",
    "bronchitis": "J40",
    "dementia": "F03.90",
    "epilepsy": "G40.909",
    "chronic fatigue": "R53.82",
    "chronic pain": "G89.29",
    "chronic kidney disease": "N18.9",
    "chronic obstructive pulmonary disease": "J44.9",
    "chronic sinusitis": "J32.9",
    "chronic liver disease": "K76.9",
    "chronic back pain": "M54.5",
    "chronic migraines": "G43.909",
    "chronic bronchitis": "J42",
    "chronic hives": "L50.9",
    "chronic urticaria": "L50.9",
    "chronic gastritis": "K29.5",
    "chronic pancreatitis": "K86.1",
    "chronic fatigue syndrome": "R53.82",
    "chronic obstructive pulmonary disease": "J44.9",
    "chronic rhinosinusitis": "J32.9",
    "chronic pelvic pain": "R10.2",
    "chronic prostatitis": "N41.9",
    "chronic pain syndrome": "G89.4",
    "chronic urticaria": "L50.9",
    "chronic sinusitis": "J32.9",
    "chronic otitis media": "H65.9",
    "chronic otitis externa": "H60.9",
    "chronic pharyngitis": "J31.2",
    "chronic tonsillitis": "J35.0",
    "chronic laryngitis": "J37.0",
    "chronic rhinitis": "J30.9",
    "chronic sinusitis": "J32.9",
    "chronic otitis media": "H65.9",
    "chronic otitis externa": "H60.9",
    "chronic pharyngitis": "J31.2",
    "chronic tonsillitis": "J35.0",
    "chronic laryngitis": "J37.0",
    "chronic rhinitis": "J30.9",
    "chronic sinusitis": "J32.9",
    "chronic otitis media": "H65.9",
    "chronic otitis externa": "H60.9",
    "chronic pharyngitis": "J31.2",
    "chronic tonsillitis": "J35.0",
    "chronic laryngitis": "J37.0",
    "flu": "J10.1",
    "pneumonia": "J18.9",
    "hemochromatosis": "E83.110",
    "scleroderma": "M34.9",
    "lupus": "M32.9",
    "sickle cell disease": "D57.1",
    "thalassemia": "D56.9",
    "cough": "R05",
    "shortness of breath": "R06.02",
    "chest pain": "R07.9",
    "fatigue": "R53.83",
    "nausea": "R11.2",
    "vomiting": "R11.2",
    "diarrhea": "R19.7",
    "constipation": "K59.00",
    "abdominal pain": "R10.9",
    "back pain": "M54.9",
    "joint pain": "M25.50",
    "muscle pain": "M79.1",
    "skin rash": "L30.9",
    "itching": "L29.9",
    "dry skin": "L85.9",
    "hair loss": "L65.9",
    "weight loss": "R63.4",
    "weight gain": "R63.5",
    "insomnia": "G47.00",
    "sleep apnea": "G47.33",
    "snoring": "R06.83",
    "night sweats": "R61.9",
    "hot flashes": "N95.1",
    "cold intolerance": "R68.84",
    "heat intolerance": "R68.84",
    # Expanded list
    "coronary artery disease": "I25.10",
    "stroke": "I63.9",
    "heart failure": "I50.9",
    "arrhythmia": "I49.9",
    "myocardial infarction": "I21.9",
    "parkinson's disease": "G20",
    "multiple sclerosis": "G35",
    "ALS": "G12.21",  # Amyotrophic lateral sclerosis
    "neuropathy": "G62.9",
    "lupus": "M32.9",
    "crohn's disease": "K50.90",
    "ulcerative colitis": "K51.90",
    "psoriasis": "L40.9",
    "celiac disease": "K90.0",
    "breast cancer": "C50.919",
    "prostate cancer": "C61",
    "lung cancer": "C34.90",
    "leukemia": "C95.90",
    "lymphoma": "C85.90",
    "HIV": "B20",
    "hepatitis B": "B16.9",
    "hepatitis C": "B18.2",
    "dengue": "A90",
    "typhoid": "A01.0",
    "influenza": "J10.1",
    "down syndrome": "Q90.9",
    "cystic fibrosis": "E84.9",
    "sickle cell anemia": "D57.1",
    "thalassemia": "D56.9",
    "hyperthyroidism": "E05.90",
    "hypothyroidism": "E03.9",
    "PCOS": "E28.2",
    "metabolic syndrome": "E88.81",
    "gout": "M10.9"
}

def get_icd10_code(disease):
    return icd10_map.get(disease.lower(), "Unknown")

def summarize_diagnosis(disease_mentions):
    summary = []
    for disease in disease_mentions:
        if not disease['negated']:
            code = get_icd10_code(disease['text'])
            summary.append({
                "disease": disease['text'],
                "icd10": code,
                "section": disease['section']
            })
    return summary

def enhanced_diagnosis(text):
    from nlp import analyze_medical_report  # Ensure nlp.py is in the same directory or importable
    
    data = analyze_medical_report(text)

    print("\n📋 CLEANED MESSAGE")
    print(data["message"])

    print("\n🧠 CONFIRMED DISEASES + ICD-10")
    confirmed = summarize_diagnosis(data["diseases_detected"])
    for item in confirmed:
        print(f"- {item['disease']} (ICD-10: {item['icd10']}, Section: {item['section']})")

    print("\n🧪 MEASUREMENTS")
    for key, value in data["measurements"].items():
        print(f"{key}: {value}")

    print("\n🧭 FUZZY DISEASE MATCHES")
    for match in data["fuzzy_matches"]:
        print(f"- {match}")

    print(f"\n👨‍⚕️ RECOMMENDED SPECIALIST: {data['suggested_specialization']}")

# Example usage
if __name__ == "__main__":
    sample_text = """
    The patient complains of chronic fatigue, nausea, and occasional vomiting.
    History includes type 2 diabetes, hypertension, and anemia. 
    Denies any cancer. BP is 138/88 mmHg. HbA1c is 8.1%.
    """
    enhanced_diagnosis(sample_text)
