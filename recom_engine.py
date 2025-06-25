import json
from diagn import enhanced_diagnosis, summarize_diagnosis, get_icd10_code
from nlp import analyze_medical_report

# Assumes the full symptoms_recommendations dictionary is already defined above.
symptoms_recommendations = {
    "Fever": [
        "Stay hydrated with water and electrolytes.",
        "Rest and avoid physical exertion.",
        "Take paracetamol or ibuprofen as advised.",
        "Monitor temperature regularly.",
        "Seek medical attention if fever persists >3 days."
    ],
    "Cold": [
        "Use saline nasal spray to relieve congestion.",
        "Stay warm and rest.",
        "Drink warm fluids like soup or tea.",
        "Use over-the-counter cold remedies cautiously.",
        "Avoid close contact to prevent spreading."
    ],
    "Flu": [
        "Rest adequately and stay in bed if needed.",
        "Drink plenty of fluids to prevent dehydration.",
        "Take antivirals if prescribed within 48 hours.",
        "Avoid public places to prevent transmission.",
        "Get annual flu vaccination."
    ],
    "Sore Throat": [
        "Gargle with warm salt water several times daily.",
        "Avoid spicy and acidic foods.",
        "Use throat lozenges or sprays.",
        "Drink warm fluids to soothe throat.",
        "Seek testing for strep if pain is severe or persists."
    ],
    "Cough": [
        "Use a humidifier to ease breathing.",
        "Drink honey with warm water or tea.",
        "Avoid smoke and pollutants.",
        "Use antitussives or expectorants as prescribed.",
        "Get evaluated for persistent cough (>3 weeks)."
    ],
    "Body Ache": [
        "Take mild pain relievers like acetaminophen.",
        "Use warm compresses or baths.",
        "Stretch and move gently if possible.",
        "Ensure proper sleep and hydration.",
        "Visit a doctor if ache persists or worsens."
    ],
    "Fatigue": [
        "Get at least 7–8 hours of sleep per night.",
        "Eat a balanced diet with iron and B12.",
        "Limit caffeine and alcohol.",
        "Break tasks into smaller, manageable goals.",
        "Screen for thyroid or anemia if persistent."
    ],
    "Headache": [
        "Apply cold or warm compresses to the head or neck.",
        "Avoid loud noise and bright light.",
        "Stay hydrated and avoid skipping meals.",
        "Try relaxation techniques like deep breathing.",
        "Consult a doctor if headaches are frequent or severe."
    ],
    "Nausea": [
        "Eat bland foods like toast or crackers.",
        "Avoid strong odors and spicy foods.",
        "Take anti-nausea meds if needed.",
        "Drink clear or ice-cold fluids slowly.",
        "Rest with head elevated."
    ],
    "Vomiting": [
        "Avoid solid food until vomiting stops.",
        "Hydrate with small sips of electrolyte fluids.",
        "Avoid dairy and heavy meals initially.",
        "Try antiemetic meds if prescribed.",
        "Seek medical help if it lasts more than 24 hours."
    ],
    "Diarrhea": [
        "Rehydrate with oral rehydration salts (ORS).",
        "Eat easily digestible food like bananas, rice.",
        "Avoid dairy and fried foods.",
        "Wash hands frequently to avoid spreading.",
        "Consult a doctor if symptoms last >2 days."
    ],
    "Constipation": [
        "Increase fiber intake (fruits, vegetables, whole grains).",
        "Drink plenty of water throughout the day.",
        "Exercise regularly.",
        "Use stool softeners if advised.",
        "Avoid processed and low-fiber foods."
    ],
    "Abdominal Pain": [
        "Avoid heavy or greasy meals.",
        "Use a warm compress on the stomach.",
        "Track pain pattern and triggers.",
        "Avoid NSAIDs unless prescribed.",
        "Seek care for sharp or persistent pain."
    ],
    "Dizziness": [
        "Sit or lie down immediately to avoid falls.",
        "Stay hydrated throughout the day.",
        "Avoid quick head movements.",
        "Eat small, frequent meals to maintain blood sugar.",
        "Consult a physician if recurring or severe."
    ],
    "Chest Pain": [
        "Stop activity and rest immediately.",
        "Avoid caffeine and stress triggers.",
        "Take nitroglycerin if prescribed.",
        "Track duration and type of pain.",
        "Seek emergency care if pain radiates or is severe."
    ],
    "Back Pain": [
        "Apply heat or cold therapy to affected area.",
        "Use ergonomic furniture or back supports.",
        "Do stretching and strengthening exercises.",
        "Avoid prolonged sitting or poor posture.",
        "Consult physiotherapy for chronic cases."
    ],
    "Joint Pain": [
        "Use warm compresses or warm baths.",
        "Take NSAIDs if recommended.",
        "Avoid high-impact activities.",
        "Maintain healthy body weight.",
        "Explore physiotherapy or joint support tools."
    ],
    "Muscle Cramps": [
        "Stretch and massage the cramped muscle.",
        "Drink fluids with electrolytes.",
        "Apply warm compress to relax the muscle.",
        "Ensure magnesium and potassium intake.",
        "Warm up before and stretch after exercise."
    ],
    "Shortness of Breath": [
        "Sit upright and practice deep breathing.",
        "Avoid exertion and allergens.",
        "Use inhalers if prescribed.",
        "Monitor oxygen saturation levels.",
        "Seek emergency care if symptoms worsen suddenly."
    ],
    "Palpitations": [
        "Practice relaxation techniques (yoga, breathing).",
        "Avoid caffeine and stimulants.",
        "Monitor heart rate and rhythm.",
        "Stay hydrated and avoid stress.",
        "See a cardiologist if frequent or prolonged."
    ],
    "Loss of Appetite": [
        "Eat small, frequent meals.",
        "Include nutrient-dense snacks.",
        "Try appealing presentation and flavors.",
        "Avoid eating alone when possible.",
        "Check for underlying issues (e.g., depression, infection)."
    ],
    "Weight Loss": [
        "Track food intake and weight regularly.",
        "Consume calorie-dense foods if unintentional.",
        "Add protein shakes or supplements.",
        "Monitor for signs of malnutrition.",
        "Seek evaluation for possible medical causes."
    ],
    "Weight Gain": [
        "Avoid sugary and processed foods.",
        "Track daily calorie intake.",
        "Engage in regular physical activity.",
        "Address emotional or binge eating triggers.",
        "Consult a dietitian for a meal plan."
    ],
    "Period Pain": [
        "Use hot water bag on lower abdomen.",
        "Take NSAIDs like ibuprofen if needed.",
        "Practice yoga or gentle stretching.",
        "Avoid caffeine and salty food.",
        "Track cycle to prepare in advance."
    ],
    "Irregular Periods": [
        "Track menstrual cycle using apps.",
        "Maintain healthy weight and reduce stress.",
        "Check for PCOS or thyroid issues.",
        "Use prescribed hormonal therapy if needed.",
        "Eat a balanced diet with healthy fats."
    ],
    "Heavy Menstrual Bleeding": [
        "Monitor pad/tampon usage and duration.",
        "Eat iron-rich foods to prevent anemia.",
        "Avoid aspirin which can increase bleeding.",
        "Consider hormonal treatment options.",
        "Consult a gynecologist for further evaluation."
    ],
    "Vaginal Discharge": [
        "Wear breathable cotton underwear.",
        "Maintain good genital hygiene.",
        "Avoid douching and scented products.",
        "Observe color/smell and note changes.",
        "Seek evaluation for infections if abnormal."
    ],
    "Night Sweats": [
        "Keep bedroom cool and ventilated.",
        "Wear breathable, moisture-wicking clothes.",
        "Avoid spicy food, alcohol before bed.",
        "Track episodes and associated symptoms.",
        "Consult a doctor to rule out infections or hormone issues."
    ],
    "Skin Rash": [
        "Avoid scratching the affected area.",
        "Use hypoallergenic moisturizers.",
        "Apply topical anti-inflammatory cream.",
        "Identify and avoid triggers (foods, fabrics).",
        "Seek medical help if rash spreads or becomes painful."
    ],
    "Itching": [
        "Apply calamine or menthol-based lotion.",
        "Keep skin moisturized and cool.",
        "Use antihistamines for allergy-induced itching.",
        "Avoid hot showers and harsh soaps.",
        "Consult doctor if persistent or severe."
    ],
    "Nosebleeds": [
        "Sit upright and lean slightly forward.",
        "Pinch nose bridge for 10 minutes.",
        "Apply a cold compress to nose.",
        "Keep nasal mucosa moist with saline.",
        "Avoid picking or blowing nose harshly."
    ],
    "Dry Mouth": [
        "Sip water regularly throughout the day.",
        "Use sugar-free lozenges or gum.",
        "Avoid caffeine, alcohol, and tobacco.",
        "Use a humidifier during sleep.",
        "Consult if persistent—may indicate medication side effects or disease."
    ],
    "Sweating Excessively": [
        "Use antiperspirants instead of deodorants.",
        "Wear loose, breathable clothes.",
        "Avoid spicy foods and caffeine.",
        "Stay hydrated to replace fluid loss.",
        "Consult for hyperhidrosis if uncontrollable."
    ],
    "Insomnia": [
        "Maintain consistent sleep-wake schedule.",
        "Avoid screens at least 1 hour before bedtime.",
        "Limit caffeine intake after 2 PM.",
        "Practice meditation or progressive muscle relaxation.",
        "Avoid napping during the day."
    ],
    "Burning Sensation in Urine": [
        "Drink plenty of water to flush bacteria.",
        "Avoid caffeine and acidic drinks.",
        "Urinate before and after sexual activity.",
        "Avoid using irritant soaps or powders in genital area.",
        "Seek evaluation for possible UTI or STIs."
    ],
    "Frequent Urination": [
        "Limit caffeine and alcohol intake.",
        "Practice bladder training techniques.",
        "Avoid drinking large amounts before bed.",
        "Monitor fluid intake throughout the day.",
        "Consult a urologist if persistent."
    ],
    "Painful Urination": [
        "Drink plenty of fluids to dilute urine.",
        "Avoid irritants like caffeine and alcohol.",
        "Use a heating pad on the lower abdomen.",
        "Consult a doctor for possible UTI or STIs.",
        "Avoid tight-fitting clothing."
    ],
    "Burning Sensation in Eyes": [
        "Avoid rubbing eyes and wash hands frequently.",
        "Use artificial tears to lubricate.",
        "Avoid contact lenses until irritation resolves.",
        "Limit screen time and use blue light filters.",
        "Consult an eye specialist if symptoms persist."
    ],
    #  Recommendations for infection and acute diseases
    "Viral Fever": [
        "Rest and stay hydrated with fluids and ORS.",
        "Take paracetamol to manage fever.",
        "Avoid crowded places to prevent spreading.",
        "Eat light and nutritious meals.",
        "Monitor temperature and symptoms regularly."
    ],
    "Dengue": [
        "Avoid NSAIDs; use only paracetamol for fever.",
        "Stay hydrated with coconut water, juices, and ORS.",
        "Monitor platelet count and hematocrit levels.",
        "Avoid mosquito bites and use repellents.",
        "Seek immediate care if bleeding or severe symptoms occur."
    ],
    "Chikungunya": [
        "Use cold or warm compresses for joint pain.",
        "Drink plenty of fluids to prevent dehydration.",
        "Take acetaminophen to reduce fever and pain.",
        "Get adequate rest during the recovery phase.",
        "Protect from mosquito exposure to prevent spread."
    ],
    "Malaria": [
        "Take prescribed antimalarial medications fully.",
        "Sleep under insecticide-treated mosquito nets.",
        "Avoid stagnant water and mosquito breeding sites.",
        "Hydrate regularly and eat balanced meals.",
        "Monitor for recurrence and complete follow-ups."
    ],
    "Typhoid": [
        "Take full course of antibiotics as prescribed.",
        "Eat soft, easily digestible food.",
        "Avoid raw fruits/vegetables and unclean water.",
        "Get adequate rest and hydration.",
        "Check for relapse during recovery phase."
    ],
    "COVID-19": [
        "Isolate and monitor symptoms for at least 5 days.",
        "Use pulse oximeter to check SpO2 regularly.",
        "Stay hydrated and maintain good nutrition.",
        "Take fever reducers like paracetamol if needed.",
        "Follow local health guidelines for testing and isolation."
    ],
    "Tuberculosis": [
        "Complete full TB treatment (6–9 months) as directed.",
        "Avoid close contact with others until non-infectious.",
        "Use masks to prevent airborne transmission.",
        "Eat a high-protein, nutrient-dense diet.",
        "Attend DOTS follow-ups and tests regularly."
    ],
    "Pneumonia": [
        "Take antibiotics and other meds as prescribed.",
        "Rest and avoid exertion during recovery.",
        "Use a humidifier to ease breathing.",
        "Stay hydrated with fluids.",
        "Seek help if breathing worsens or fever persists."
    ],
    "Bronchitis": [
        "Avoid smoke and irritants; use air purifiers if needed.",
        "Stay hydrated to loosen mucus.",
        "Use prescribed inhalers or cough suppressants.",
        "Rest and avoid cold air.",
        "Complete antibiotics if bacterial cause suspected."
    ],
    "Sinusitis": [
        "Use saline nasal sprays and steam inhalation.",
        "Stay hydrated to thin mucus.",
        "Avoid allergens and pollutants.",
        "Use antibiotics if prescribed for bacterial cases.",
        "Elevate your head while sleeping."
    ],
    "Tonsillitis": [
        "Gargle with warm salt water frequently.",
        "Avoid spicy, rough, or acidic foods.",
        "Take antibiotics or antivirals as prescribed.",
        "Use throat lozenges and pain relievers.",
        "Rest voice and avoid talking too much."
    ],
    "Ear Infection": [
        "Use prescribed eardrops and medications.",
        "Avoid inserting anything into the ear.",
        "Keep ears dry during showers or swimming.",
        "Use warm compress for ear pain relief.",
        "Consult ENT if recurrent or severe."
    ],
    "Conjunctivitis": [
        "Avoid touching/rubbing the eyes.",
        "Use antibiotic or antihistamine eye drops as prescribed.",
        "Wash hands frequently and avoid sharing items.",
        "Clean discharge with warm water gently.",
        "Avoid contact lenses until symptoms resolve."
    ],
    "Strep Throat": [
        "Complete the full antibiotic course.",
        "Avoid close contact to prevent transmission.",
        "Gargle with salt water to relieve throat pain.",
        "Avoid smoking and alcohol.",
        "Replace toothbrush after infection clears."
    ],
    "UTI": [
        "Drink plenty of water to flush bacteria.",
        "Urinate frequently and do not hold urine.",
        "Take full antibiotic course as prescribed.",
        "Avoid perfumed soaps in the genital area.",
        "Wipe front to back after using the toilet."
    ],
    "Vaginal Yeast Infection": [
        "Use prescribed antifungal creams or pills.",
        "Wear loose, breathable cotton underwear.",
        "Avoid scented hygiene products.",
        "Maintain proper genital hygiene.",
        "Avoid douching or excessive washing."
    ],
    "Bacterial Vaginosis": [
        "Complete the antibiotic treatment.",
        "Avoid scented products near genital area.",
        "Use protection during intercourse.",
        "Avoid douching which disrupts flora.",
        "Maintain regular gynecological checkups."
    ],
    "Skin Infection": [
        "Keep the affected area clean and dry.",
        "Apply topical or oral antibiotics as needed.",
        "Avoid scratching to prevent spread.",
        "Cover wound with sterile dressing if needed.",
        "Monitor for pus, redness, or spreading."
    ],
    "Gastroenteritis": [
        "Hydrate with ORS to replace fluid loss.",
        "Eat light, bland foods like rice, toast, banana.",
        "Avoid dairy, caffeine, and fatty foods.",
        "Rest to support immune recovery.",
        "Wash hands frequently to avoid spreading."
    ],
    "Hepatitis A": [
        "Avoid alcohol and fatty foods.",
        "Eat a balanced, liver-friendly diet.",
        "Get plenty of rest during recovery.",
        "Wash hands thoroughly after bathroom use.",
        "Ensure safe drinking water and clean food."
    ],
    "Hepatitis B": [
        "Avoid alcohol and hepatotoxic medications.",
        "Follow antiviral treatment if prescribed.",
        "Monitor liver function tests regularly.",
        "Practice safe sex and avoid blood contact.",
        "Get vaccinated if not immune."
    ],
    "Hepatitis C": [
        "Take antiviral therapy as recommended.",
        "Avoid alcohol and processed foods.",
        "Undergo regular liver function monitoring.",
        "Do not share razors, toothbrushes, or needles.",
        "Avoid over-the-counter pain meds without advice."
    ],
    "HIV": [
        "Adhere strictly to ART medication schedule.",
        "Avoid sharing needles or unprotected sex.",
        "Maintain regular CD4 and viral load testing.",
        "Eat a nutritious diet to support immunity.",
        "Manage stress and mental health proactively."
    ],
    "STIs": [
        "Use condoms to prevent transmission.",
        "Avoid sexual activity until cleared by doctor.",
        "Notify and treat all partners.",
        "Follow antibiotic or antiviral treatment fully.",
        "Attend regular screenings if sexually active."
    ],
    "Genital Herpes": [
        "Take antiviral medication during outbreaks.",
        "Avoid skin-to-skin contact during symptoms.",
        "Maintain hygiene and wear loose clothing.",
        "Reduce stress which can trigger outbreaks.",
        "Stay in regular follow-up with a specialist."
    ],
    "Scabies": [
        "Use prescribed scabicidal cream over entire body.",
        "Wash clothes, bedding in hot water.",
        "Avoid close contact with others during treatment.",
        "Treat all household contacts.",
        "Repeat treatment if advised after 1 week."
    ],
    "Chickenpox": [
        "Avoid scratching; trim nails to prevent infection.",
        "Apply calamine lotion or take antihistamines.",
        "Stay isolated until all blisters crust over.",
        "Rest and drink plenty of fluids.",
        "Take paracetamol for fever (avoid aspirin)."
    ],
    "Measles": [
        "Ensure rest and hydration.",
        "Use vitamin A supplements if advised.",
        "Treat fever with acetaminophen.",
        "Isolate to prevent spread to others.",
        "Get vaccinated to prevent future outbreaks."
    ],
    "Mumps": [
        "Apply ice packs to swollen glands.",
        "Eat soft foods and avoid sour items.",
        "Use pain relievers to reduce discomfort.",
        "Stay home for at least 5 days after onset.",
        "Get MMR vaccine if not vaccinated."
    ],
    "Ringworm": [
        "Apply antifungal creams to affected area.",
        "Keep area clean and dry at all times.",
        "Avoid sharing towels or clothing.",
        "Wear loose, breathable fabrics.",
        "Continue treatment for full duration even after symptoms clear."
    ],
    "Jaundice": [
        "Eat a liver-friendly diet low in fat.",
        "Avoid alcohol and unnecessary medications.",
        "Stay hydrated and rest adequately.",
        "Monitor bilirubin and liver enzymes.",
        "Seek treatment for the underlying cause."
    ],
    # recommendation for Chronic & Systemic Diseases
    "Diabetes": [
        "Monitor blood sugar levels regularly.",
        "Follow a low-glycemic, high-fiber diet.",
        "Exercise 30 minutes most days of the week.",
        "Take medications or insulin as prescribed.",
        "Schedule regular HbA1c tests and eye exams."
    ],
    "Hypertension": [
        "Reduce sodium intake to <1500 mg/day.",
        "Engage in regular aerobic exercise.",
        "Monitor BP at home regularly.",
        "Limit alcohol and avoid smoking.",
        "Follow the DASH or Mediterranean diet."
    ],
    "Hypothyroidism": [
        "Take levothyroxine on an empty stomach daily.",
        "Avoid soy and high-fiber meals around medication time.",
        "Monitor TSH levels every 6-12 months.",
        "Watch for fatigue, weight gain, and cold intolerance.",
        "Maintain consistent medication timing."
    ],
    "Hyperthyroidism": [
        "Take antithyroid medication consistently.",
        "Avoid iodine-rich foods if advised.",
        "Monitor thyroid function (TSH, T3, T4) regularly.",
        "Report palpitations, heat intolerance to doctor.",
        "Consider definitive treatment (RAI or surgery) if persistent."
    ],
    "High Cholesterol": [
        "Reduce saturated and trans fats in the diet.",
        "Increase intake of fiber-rich foods and omega-3.",
        "Exercise 150 minutes/week.",
        "Take statins or other lipid-lowering drugs if prescribed.",
        "Monitor lipid profile regularly."
    ],
    "Obesity": [
        "Follow a calorie-controlled, nutrient-dense meal plan.",
        "Exercise most days with cardio and strength training.",
        "Avoid processed and sugary foods.",
        "Address emotional or binge eating behavior.",
        "Seek medical/surgical options for severe obesity."
    ],
    "PCOS": [
        "Maintain healthy weight through diet and exercise.",
        "Use hormonal therapy to regulate cycles if advised.",
        "Limit refined carbohydrates and sugar.",
        "Manage acne/hirsutism with medication if needed.",
        "Screen for insulin resistance and fertility issues."
    ],
    "Endometriosis": [
        "Track symptoms and menstrual cycles.",
        "Use NSAIDs for pain relief during menstruation.",
        "Consider hormonal therapy to control growth.",
        "Maintain physical activity and stress relief.",
        "Surgical options may be needed for severe cases."
    ],
    "Anemia": [
        "Consume iron-rich foods like meat, legumes, spinach.",
        "Take iron supplements as advised (on empty stomach).",
        "Avoid tea/coffee near mealtime to enhance iron absorption.",
        "Include vitamin C to boost iron absorption.",
        "Test hemoglobin and ferritin levels regularly."
    ],
    "Vitamin D Deficiency": [
        "Get sunlight exposure (10–20 min/day).",
        "Take vitamin D3 supplements regularly.",
        "Include fortified foods and fatty fish in diet.",
        "Test serum vitamin D levels periodically.",
        "Combine with calcium for bone support."
    ],
    "Vitamin B12 Deficiency": [
        "Eat B12-rich foods (meat, dairy, eggs).",
        "Take oral or injectable B12 as prescribed.",
        "Treat underlying absorption issues (e.g., pernicious anemia).",
        "Check CBC and B12 levels periodically.",
        "Watch for fatigue, tingling, memory issues."
    ],
    "Osteoporosis": [
        "Consume calcium and vitamin D daily.",
        "Engage in weight-bearing exercises (walking, lifting).",
        "Avoid smoking and excessive alcohol.",
        "Use bisphosphonates or other meds if prescribed.",
        "Prevent falls with home safety and mobility aids."
    ],
    "Rheumatoid Arthritis": [
        "Start DMARDs early to control disease progression.",
        "Use warm packs and stretching for joint flexibility.",
        "Manage fatigue and energy with pacing strategies.",
        "Regular checkups with a rheumatologist.",
        "Monitor for medication side effects (e.g., MTX)."
    ],
    "Osteoarthritis": [
        "Maintain healthy body weight to reduce joint stress.",
        "Use physical therapy and low-impact exercises.",
        "Take NSAIDs or topical pain relievers as needed.",
        "Use assistive devices for severe joint damage.",
        "Consider joint replacement for end-stage cases."
    ],
    "Asthma": [
        "Avoid known allergens and irritants.",
        "Use inhalers as prescribed (rescue and maintenance).",
        "Track symptoms using a peak flow meter.",
        "Get annual flu and pneumonia vaccines.",
        "Create and follow an asthma action plan."
    ],
    "COPD": [
        "Stop smoking immediately if applicable.",
        "Use bronchodilators and inhaled steroids regularly.",
        "Join pulmonary rehab and do breathing exercises.",
        "Vaccinate against flu, COVID-19, and pneumonia.",
        "Monitor oxygen levels and avoid high altitudes."
    ],
    "Chronic Sinusitis": [
        "Use saline nasal irrigation daily.",
        "Avoid allergens, pollution, and cold air.",
        "Take decongestants or corticosteroids as needed.",
        "Consider CT scan or ENT evaluation for surgery.",
        "Keep air humidified indoors."
    ],
    "GERD": [
        "Avoid trigger foods (spicy, acidic, caffeine).",
        "Elevate head of bed while sleeping.",
        "Don’t lie down immediately after eating.",
        "Take PPIs or H2 blockers if prescribed.",
        "Maintain healthy weight to reduce reflux."
    ],
    "Gastritis": [
        "Avoid NSAIDs and alcohol.",
        "Eat smaller, more frequent meals.",
        "Limit spicy and acidic foods.",
        "Use antacids or PPIs as prescribed.",
        "Test and treat H. pylori if suspected."
    ],
    "Peptic Ulcer": [
        "Take prescribed antibiotics and PPIs completely.",
        "Avoid NSAIDs, alcohol, and smoking.",
        "Eat non-irritating, bland meals.",
        "Reduce stress with relaxation techniques.",
        "Follow up with endoscopy if symptoms persist."
    ],
    "IBS": [
        "Identify and avoid trigger foods (e.g., FODMAPs).",
        "Maintain regular meal timings and hydration.",
        "Use fiber supplements or antispasmodics as needed.",
        "Manage stress via CBT or mindfulness.",
        "Track symptoms using a bowel diary."
    ],
    "IBD": [
        "Take anti-inflammatory or immunosuppressive meds regularly.",
        "Avoid NSAIDs and lactose-rich foods.",
        "Monitor weight and nutritional status.",
        "Track flares and consult doctor promptly.",
        "Consider surgery if complications arise."
    ],
    "Crohn’s Disease": [
        "Follow anti-inflammatory diet (low residue).",
        "Use corticosteroids, immunomodulators as prescribed.",
        "Stay up to date on vaccinations.",
        "Monitor for anemia and vitamin deficiencies.",
        "Seek surgical consult if bowel damage is severe."
    ],
    "Ulcerative Colitis": [
        "Take mesalamine or biologics consistently.",
        "Avoid high-fiber and lactose-rich foods during flares.",
        "Hydrate adequately and avoid caffeine.",
        "Monitor for bleeding and anemia.",
        "Routine colonoscopies to screen for dysplasia."
    ],
    "Celiac Disease": [
        "Follow a strict gluten-free diet lifelong.",
        "Read food labels for hidden gluten.",
        "Consult a dietitian for nutrition guidance.",
        "Watch for signs of malabsorption.",
        "Monitor vitamin and mineral levels regularly."
    ],
    "Fatty Liver Disease": [
        "Adopt low-carb, low-sugar diet.",
        "Lose 5–10% of body weight to reverse damage.",
        "Avoid alcohol completely.",
        "Exercise regularly to reduce liver fat.",
        "Check liver enzymes and ultrasound periodically."
    ],
    "Liver Cirrhosis": [
        "Avoid alcohol and hepatotoxic meds.",
        "Eat low-sodium diet to manage ascites.",
        "Monitor for varices, hepatic encephalopathy.",
        "Attend regular liver function and imaging tests.",
        "Consider transplant evaluation for advanced cases."
    ],
    "CKD": [
        "Limit protein, potassium, and phosphorus in diet.",
        "Monitor creatinine, GFR, and electrolytes regularly.",
        "Control BP and blood sugar strictly.",
        "Avoid nephrotoxic medications and contrast dyes.",
        "Consult nephrologist early for disease staging."
    ],
    "Kidney Stones": [
        "Drink 2–3 liters of water daily.",
        "Reduce salt and oxalate-rich foods.",
        "Avoid excessive animal protein.",
        "Take prescribed medication to prevent recurrence.",
        "Strain urine to catch stone for analysis."
    ],
    "Gallstones": [
        "Avoid fatty and fried foods.",
        "Eat regular, balanced meals (don’t skip).",
        "Lose weight gradually if overweight.",
        "Consider surgery for symptomatic stones.",
        "Monitor for pain in upper right abdomen."
    ],
    "Migraine": [
        "Track triggers and avoid them (light, food, stress).",
        "Use triptans or NSAIDs during attack onset.",
        "Maintain regular sleep and eating habits.",
        "Consider preventive meds if frequent.",
        "Practice relaxation and reduce screen time."
    ],
    "Epilepsy": [
        "Take antiepileptic drugs consistently.",
        "Avoid triggers like flashing lights and lack of sleep.",
        "Inform family/friends about first aid steps.",
        "Wear medical alert identification.",
        "Regular neurologist follow-ups and EEGs."
    ],
    "Parkinson’s Disease": [
        "Take dopaminergic medications on schedule.",
        "Exercise to maintain mobility and coordination.",
        "Use physical and occupational therapy.",
        "Watch for swallowing or balance problems.",
        "Maintain a high-fiber diet to prevent constipation."
    ],
    "Alzheimer’s Disease": [
        "Ensure a structured routine with reminders.",
        "Engage in cognitive stimulation activities.",
        "Provide emotional support and safety supervision.",
        "Take cholinesterase inhibitors if prescribed.",
        "Get caregiver support for long-term planning."
    ],
    "Multiple Sclerosis": [
        "Use immunomodulators to slow disease progression.",
        "Balance rest and activity to avoid fatigue.",
        "Manage stress with support groups or therapy.",
        "Exercise regularly to maintain function.",
        "Monitor for relapses and consult neurologist."
    ],
    "Lupus": [
        "Avoid sun exposure and use SPF regularly.",
        "Take immunosuppressants or antimalarials as prescribed.",
        "Track flares and symptoms in a journal.",
        "Rest during fatigue and avoid overexertion.",
        "Follow up with labs to monitor organ function."
    ],
    "Fibromyalgia": [
        "Follow regular sleep and exercise schedule.",
        "Use cognitive-behavioral therapy (CBT) for coping.",
        "Try yoga, tai chi, or water aerobics.",
        "Use pain relievers and antidepressants as needed.",
        "Avoid stress and overstimulation."
    ],
    "Scleroderma": [
        "Moisturize skin regularly and avoid cold exposure.",
        "Treat reflux and gastrointestinal symptoms promptly.",
        "Monitor lung and kidney function regularly.",
        "Use immunosuppressive therapy if advised.",
        "Stay active to prevent joint stiffness."
    ],
    "Psoriasis": [
        "Use topical corticosteroids or moisturizers.",
        "Avoid triggers like stress, cold, or injury.",
        "Follow a healthy, anti-inflammatory diet.",
        "Consider phototherapy or biologics for severe cases.",
        "Keep skin hydrated and avoid harsh soaps."
    ],
    # Recommendation for  Cardiac, Respiratory, Neuro
    "Coronary Artery Disease": [
        "Follow a heart-healthy diet low in saturated fat.",
        "Take prescribed statins and antiplatelet meds.",
        "Quit smoking and limit alcohol consumption.",
        "Exercise regularly with your doctor’s approval.",
        "Attend routine heart checkups and stress tests."
    ],
    "Heart Attack": [
        "Take medications like aspirin, beta-blockers, or ACE inhibitors.",
        "Adopt a low-fat, low-sodium diet.",
        "Rehabilitate with supervised cardiac exercises.",
        "Monitor blood pressure and cholesterol levels.",
        "Seek emergency help if chest pain recurs."
    ],
    "Stroke": [
        "Undergo physical and speech therapy as needed.",
        "Control hypertension, diabetes, and cholesterol.",
        "Take blood thinners or antiplatelets as prescribed.",
        "Adopt a Mediterranean-style diet.",
        "Avoid smoking and monitor for stroke warning signs."
    ],
    "Heart Failure": [
        "Reduce fluid and sodium intake as advised.",
        "Take diuretics and other meds on time.",
        "Track daily weight and report sudden changes.",
        "Avoid strenuous activity unless approved.",
        "Attend follow-up visits for echocardiography and labs."
    ],
    "Arrhythmia": [
        "Avoid caffeine, alcohol, and stress triggers.",
        "Monitor pulse regularly at home.",
        "Take anti-arrhythmic drugs as prescribed.",
        "Use a Holter monitor if recommended.",
        "Consider ablation or pacemaker if persistent."
    ],
    "Atrial Fibrillation": [
        "Use blood thinners to reduce stroke risk.",
        "Monitor pulse and blood pressure regularly.",
        "Avoid stimulants like caffeine and decongestants.",
        "Limit alcohol intake and stress.",
        "Consult about cardioversion or ablation options."
    ],
    "Anxiety Disorder": [
        "Practice relaxation techniques like deep breathing.",
        "Limit caffeine and avoid recreational drugs.",
        "Attend CBT or other forms of therapy.",
        "Consider SSRIs or other medications if needed.",
        "Establish a structured daily routine."
    ],
    "Depression": [
        "Engage in regular physical activity.",
        "Stick to a sleep and eating schedule.",
        "Avoid isolation and seek social support.",
        "Use antidepressants or therapy as advised.",
        "Monitor and report suicidal thoughts or worsening mood."
    ],
    "Panic Disorder": [
        "Use breathing techniques during panic attacks.",
        "Avoid caffeine, alcohol, and sleep deprivation.",
        "Identify and challenge negative thoughts.",
        "Attend cognitive-behavioral therapy regularly.",
        "Consider medications like SSRIs or benzodiazepines under supervision."
    ],
    "PTSD": [
        "Attend trauma-focused therapy (CBT or EMDR).",
        "Build a strong support system.",
        "Practice grounding and mindfulness exercises.",
        "Avoid triggers and substance use.",
        "Take medications as prescribed for mood/sleep."
    ],
    "Schizophrenia": [
        "Follow antipsychotic medication schedule strictly.",
        "Maintain regular psychiatric follow-ups.",
        "Avoid alcohol and recreational drug use.",
        "Engage in structured daily routines.",
        "Ensure support from caregivers and counselors."
    ],
    "Bipolar Disorder": [
        "Stick to mood stabilizer regimen without skipping doses.",
        "Avoid alcohol and sleep disruption.",
        "Monitor mood patterns using a journal or app.",
        "Attend therapy to build coping strategies.",
        "Have an emergency plan for manic or depressive episodes."
    ],
    "ADHD": [
        "Use timers or planners to stay organized.",
        "Practice mindfulness to improve focus.",
        "Take stimulant or non-stimulant meds as prescribed.",
        "Break tasks into smaller, manageable steps.",
        "Get regular feedback from teachers/therapists."
    ],
    "Autism Spectrum Disorder": [
        "Enroll in speech and occupational therapy early.",
        "Use visual schedules and routines.",
        "Work with behavioral therapists (ABA, CBT).",
        "Encourage sensory-safe environments.",
        "Promote social skills through structured play."
    ],
    "Sleep Apnea": [
        "Use CPAP machine as directed every night.",
        "Maintain a healthy weight.",
        "Avoid alcohol and sedatives before bedtime.",
        "Sleep on your side instead of your back.",
        "Have regular follow-up with a sleep specialist."
    ],
    # Recommendation for Women’s Health
    "Menopause": [
        "Manage hot flashes with cooling strategies and lifestyle changes.",
        "Take calcium and vitamin D to prevent osteoporosis.",
        "Exercise regularly to reduce mood swings and weight gain.",
        "Consider HRT (Hormone Replacement Therapy) under medical supervision.",
        "Practice pelvic floor exercises to reduce urinary symptoms."
    ],
    "Hormonal Imbalance": [
        "Get hormone levels tested regularly.",
        "Maintain a balanced diet with essential fats and micronutrients.",
        "Limit processed foods and sugar to stabilize hormones.",
        "Reduce stress through meditation or yoga.",
        "Follow medical advice on hormonal therapies if needed."
    ],
    "Infertility (Female)": [
        "Track ovulation using apps or ovulation kits.",
        "Maintain healthy body weight and nutrition.",
        "Avoid smoking, alcohol, and excessive caffeine.",
        "Consult a reproductive endocrinologist.",
        "Manage stress and consider support counseling."
    ],
    "PMS": [
        "Eat small, frequent meals and avoid sugar and caffeine.",
        "Exercise regularly to reduce cramps and mood symptoms.",
        "Use NSAIDs for pain relief if needed.",
        "Practice relaxation techniques like yoga.",
        "Consider calcium and magnesium supplements."
    ],
    "Breast Lumps": [
        "Schedule a clinical breast exam.",
        "Get a mammogram or ultrasound as advised.",
        "Avoid caffeine if lumps are fibrocystic.",
        "Track any changes in size or pain.",
        "Follow up with biopsy if suggested."
    ],
    "Ovarian Cysts": [
        "Use pain relief medications as prescribed.",
        "Get regular pelvic ultrasounds.",
        "Monitor for signs of rupture or torsion.",
        "Track your menstrual cycle.",
        "Follow up with a gynecologist for persistent cysts."
    ],
    "Cervical Cancer": [
        "Get regular Pap smears and HPV tests.",
        "Take the HPV vaccine if eligible.",
        "Stop smoking to reduce risk.",
        "Use barrier methods during intercourse.",
        "Follow treatment protocols (surgery, chemo, radiation)."
    ],
    "Uterine Fibroids": [
        "Monitor fibroid size and symptoms with ultrasound.",
        "Take medications to manage bleeding or pain.",
        "Consider hormone therapy if symptoms are severe.",
        "Use iron supplements if anemic.",
        "Discuss surgical options like myomectomy with a gynecologist."
    ],

    # Men’s Health
    "Erectile Dysfunction": [
        "Limit alcohol and avoid smoking.",
        "Maintain a healthy weight and regular exercise.",
        "Manage stress and mental health.",
        "Check testosterone levels if persistent.",
        "Use medications like sildenafil under medical advice."
    ],
    "Premature Ejaculation": [
        "Practice pelvic floor exercises.",
        "Use behavioral techniques like stop-start method.",
        "Try desensitizing creams or condoms.",
        "Consult a sex therapist.",
        "Consider medications like SSRIs if prescribed."
    ],
    "Infertility (Male)": [
        "Avoid heat exposure (hot tubs, tight underwear).",
        "Limit alcohol, tobacco, and drug use.",
        "Check for varicocele or hormonal imbalance.",
        "Take supplements like zinc and folic acid.",
        "Consult a urologist or fertility specialist."
    ],
    "Prostate Enlargement": [
        "Reduce intake of caffeine and alcohol.",
        "Void bladder fully and on schedule.",
        "Use alpha-blockers or 5-ARIs if prescribed.",
        "Monitor symptoms with regular checkups.",
        "Consider minimally invasive procedures if needed."
    ],
    "Prostate Cancer": [
        "Get regular PSA tests after age 50 (or earlier if high-risk).",
        "Maintain a diet rich in vegetables and low in red meat.",
        "Follow active surveillance or treatment plan as advised.",
        "Attend all oncology follow-ups.",
        "Discuss radiation or surgical options thoroughly."
    ],

    # Pediatric & Geriatric
    "Iron Deficiency in Children": [
        "Provide iron-rich foods (meat, legumes, fortified cereals).",
        "Use iron drops or syrup as prescribed.",
        "Avoid giving milk around meal time.",
        "Combine iron with vitamin C for better absorption.",
        "Monitor weight and developmental milestones."
    ],
    "Growth Delay": [
        "Ensure adequate calories, protein, and micronutrients.",
        "Rule out endocrine or genetic disorders.",
        "Track height and weight percentiles.",
        "Encourage regular physical activity.",
        "Consult a pediatric endocrinologist."
    ],
    "Childhood Obesity": [
        "Encourage home-cooked, low-sugar meals.",
        "Limit screen time and promote outdoor play.",
        "Involve the whole family in healthy routines.",
        "Avoid sugary drinks and processed snacks.",
        "Consult a pediatric dietitian if needed."
    ],
    "Bedwetting": [
        "Avoid fluids 1–2 hours before bedtime.",
        "Use bedwetting alarms for older children.",
        "Ensure child voids bladder before bed.",
        "Reassure the child—avoid punishment.",
        "Seek medical evaluation for underlying causes."
    ],
    "ADHD in Kids": [
        "Use positive reinforcement and structured routines.",
        "Follow behavioral therapy interventions.",
        "Minimize distractions during study time.",
        "Provide breaks and sensory tools.",
        "Use stimulant medications only under supervision."
    ],
    "Autism": [
        "Begin speech and occupational therapy early.",
        "Use visual supports and structured environments.",
        "Practice daily routines consistently.",
        "Encourage social interactions in a safe setting.",
        "Consult developmental pediatrician for support."
    ],
    "Aging-Related Memory Loss": [
        "Engage in mental stimulation (games, reading).",
        "Stay socially and physically active.",
        "Eat a brain-healthy diet (e.g., Mediterranean).",
        "Control chronic diseases like diabetes and BP.",
        "Get evaluated for dementia if memory worsens."
    ],
    "Falls in Elderly": [
        "Remove trip hazards at home (rugs, cords).",
        "Use grab bars and non-slip mats in bathrooms.",
        "Encourage strength and balance exercises.",
        "Review medications for side effects.",
        "Have vision and hearing checked regularly."
    ],

    # Oncology
    "Breast Cancer": [
        "Follow oncologist-directed treatment (surgery, chemo, radiation).",
        "Perform regular breast self-exams.",
        "Attend all scheduled follow-ups and mammograms.",
        "Eat a balanced, nutrient-rich diet.",
        "Join support groups or counseling if needed."
    ],
    "Lung Cancer": [
        "Quit smoking and avoid passive smoke.",
        "Follow chemo/radiation or immunotherapy plan.",
        "Monitor for new symptoms (cough, weight loss).",
        "Eat high-protein meals to maintain weight.",
        "Seek palliative care support for symptom relief."
    ],
    "Colon Cancer": [
        "Get colonoscopy screening starting age 45–50.",
        "Eat high-fiber, low-fat diet.",
        "Avoid processed meats and alcohol.",
        "Take chemo/radiation as prescribed.",
        "Report rectal bleeding or changes in bowel habits."
    ],
    "Skin Cancer": [
        "Use SPF 30+ sunscreen daily.",
        "Avoid tanning beds and peak sun exposure.",
        "Check moles and skin changes monthly.",
        "Get suspicious lesions biopsied promptly.",
        "Wear protective clothing and hats outdoors."
    ],
    "Leukemia": [
        "Follow chemotherapy or bone marrow transplant protocols.",
        "Avoid infections with good hygiene and masks.",
        "Get regular CBC and bone marrow evaluations.",
        "Report fevers or bleeding immediately.",
        "Consult oncology team for support services."
    ],
    "Pancreatic Cancer": [
        "Follow personalized oncology treatment plan.",
        "Manage weight and appetite with a dietitian.",
        "Control pain and digestive symptoms with medications.",
        "Attend all imaging and blood work sessions.",
        "Seek psychological and palliative support early."
    ],
    "Brain Tumor": [
        "Take anticonvulsants and steroids if prescribed.",
        "Follow up on MRI/CT and neurological assessments.",
        "Rehabilitate with physical and occupational therapy.",
        "Report any new neurological symptoms.",
        "Discuss surgical, chemo, or radiotherapy options."
    ],

    # Eye, Ear, Skin
    "Cataract": [
        "Use brighter lights for reading and activities.",
        "Wear UV-protective sunglasses.",
        "Schedule regular eye check-ups.",
        "Avoid night driving if vision is impaired.",
        "Plan cataract surgery if vision worsens."
    ],
    "Glaucoma": [
        "Use prescribed eye drops regularly.",
        "Avoid medications that raise eye pressure.",
        "Get intraocular pressure (IOP) checked periodically.",
        "Inform doctor of any vision changes.",
        "Consider laser or surgical options if needed."
    ],
    "Eczema": [
        "Moisturize skin several times a day.",
        "Use fragrance-free and hypoallergenic products.",
        "Avoid known irritants like wool and dust.",
        "Apply corticosteroid creams as prescribed.",
        "Manage stress to reduce flare-ups."
    ],
    "Dandruff": [
        "Use medicated anti-dandruff shampoo regularly.",
        "Avoid hair products with alcohol.",
        "Massage scalp gently to reduce flakes.",
        "Maintain a healthy, balanced diet.",
        "Consult a dermatologist if severe or persistent."
    ]
}
def generate_recommendations(diseases: list) -> dict:
    results = {}
    for item in diseases:
        disease_input = item["disease"].strip().lower()
        match = next(
            (key for key in symptoms_recommendations.keys() if key.lower() == disease_input),
            None
        )
        recommendations = symptoms_recommendations.get(match, ["Consult a specialist for personalized guidance."])
        results[item["disease"]] = recommendations
    return results

def advanced_report(text):
    print("📥 ANALYZING REPORT...")
    nlp_data = analyze_medical_report(text)
    confirmed_diseases = summarize_diagnosis(nlp_data["diseases_detected"])

    print("\n✅ CONFIRMED CONDITIONS:")
    for d in confirmed_diseases:
        print(f"- {d['disease']}")

    recommendations = generate_recommendations(confirmed_diseases)

    print("\n📌 PERSONALIZED RECOMMENDATIONS:")
    for disease, recs in recommendations.items():
        print(f"\n🔹 {disease.title()}")
        for rec in recs:
            print(f"  - {rec}")

    return recommendations

# Example test
if __name__ == "__main__":
    report_text = """
    The patient complains of chronic fatigue, nausea, and occasional vomiting.
    History includes type 2 diabetes, hypertension, and anemia. 
    Denies any cancer. BP is 138/88 mmHg. HbA1c is 8.1%.
    """
    advanced_report(report_text)
