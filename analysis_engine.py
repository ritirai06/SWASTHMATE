"""
Enhanced Analysis Engine for Medical Reports
Provides comprehensive analysis, priority recommendations, and drug interaction checking
"""
from typing import Dict, List, Any, Tuple, Optional
import re

class EnhancedAnalysisEngine:
    def __init__(self):
        """Initialize the enhanced analysis engine"""
        self.drug_interactions_db = self._load_drug_interactions()
        self.normal_ranges = self._load_normal_ranges()
    
    def _load_normal_ranges(self) -> Dict[str, Dict[str, Any]]:
        """Load normal reference ranges for lab tests"""
        return {
            # Hematology
            "Hemoglobin": {"min": 13.5, "max": 17.5, "unit": "g/dL", "gender_specific": True, "male": {"min": 13.5, "max": 17.5}, "female": {"min": 12.0, "max": 15.5}},
            "Total Leukocyte Count": {"min": 4000, "max": 11000, "unit": "cells/cumm"},
            "Total RBC Count": {"min": 4.5, "max": 5.5, "unit": "million/cumm", "gender_specific": True, "male": {"min": 4.5, "max": 5.5}, "female": {"min": 4.0, "max": 5.0}},
            "Platelet Count": {"min": 150000, "max": 450000, "unit": "lakh/cumm"},
            "Hematocrit (HCT)": {"min": 40, "max": 50, "unit": "%", "gender_specific": True, "male": {"min": 40, "max": 50}, "female": {"min": 36, "max": 46}},
            "MCV": {"min": 80, "max": 100, "unit": "fL"},
            "MCH": {"min": 27, "max": 32, "unit": "pg"},
            "MCHC": {"min": 32, "max": 36, "unit": "g/dL"},
            "Neutrophils": {"min": 40, "max": 70, "unit": "%"},
            "Lymphocytes": {"min": 20, "max": 40, "unit": "%"},
            "Monocytes": {"min": 2, "max": 8, "unit": "%"},
            "Eosinophils": {"min": 1, "max": 4, "unit": "%"},
            "Basophils": {"min": 0, "max": 1, "unit": "%"},
            
            # Diabetes
            "Glucose": {"min": 70, "max": 100, "unit": "mg/dL"},
            "HbA1c": {"min": 4.0, "max": 5.6, "unit": "%"},
            
            # Lipid Profile
            "Total Cholesterol": {"min": 125, "max": 200, "unit": "mg/dL"},
            "HDL Cholesterol": {"min": 40, "max": 60, "unit": "mg/dL", "higher_better": True},
            "LDL Cholesterol": {"min": 0, "max": 130, "unit": "mg/dL"},
            "Triglycerides": {"min": 0, "max": 150, "unit": "mg/dL"},
            
            # Liver Function
            "SGPT (ALT)": {"min": 7, "max": 56, "unit": "U/L"},
            "SGOT (AST)": {"min": 10, "max": 40, "unit": "U/L"},
            "ALP": {"min": 44, "max": 147, "unit": "U/L"},
            "Bilirubin Total": {"min": 0.3, "max": 1.2, "unit": "mg/dL"},
            "Bilirubin Direct": {"min": 0, "max": 0.3, "unit": "mg/dL"},
            "Albumin": {"min": 3.5, "max": 5.0, "unit": "g/dL"},
            
            # Kidney Function
            "Serum Creatinine": {"min": 0.6, "max": 1.2, "unit": "mg/dL", "gender_specific": True, "male": {"min": 0.7, "max": 1.3}, "female": {"min": 0.6, "max": 1.1}},
            "BUN": {"min": 7, "max": 20, "unit": "mg/dL"},
            "Urea": {"min": 15, "max": 40, "unit": "mg/dL"},
            "eGFR": {"min": 90, "max": 120, "unit": "mL/min/1.73m²"},
            
            # Electrolytes
            "Sodium": {"min": 136, "max": 145, "unit": "mmol/L"},
            "Potassium": {"min": 3.5, "max": 5.0, "unit": "mmol/L"},
            "Calcium": {"min": 8.5, "max": 10.5, "unit": "mg/dL"},
            "Phosphate": {"min": 2.5, "max": 4.5, "unit": "mg/dL"},
            "Magnesium": {"min": 1.7, "max": 2.2, "unit": "mg/dL"},
            "Chloride": {"min": 98, "max": 107, "unit": "mmol/L"},
            
            # Thyroid
            "TSH": {"min": 0.4, "max": 4.0, "unit": "µIU/mL"},
            "T3": {"min": 80, "max": 200, "unit": "ng/dL"},
            "T4": {"min": 5.0, "max": 12.0, "unit": "µg/dL"},
            
            # Vitamins
            "Vitamin D": {"min": 30, "max": 100, "unit": "ng/mL"},
            "Vitamin B12": {"min": 200, "max": 900, "unit": "pg/mL"},
            
            # Cardiac Markers
            "Troponin": {"min": 0, "max": 0.04, "unit": "ng/mL"},
            "CRP": {"min": 0, "max": 3, "unit": "mg/L"},
            "ESR": {"min": 0, "max": 20, "unit": "mm/hr", "gender_specific": True, "male": {"min": 0, "max": 15}, "female": {"min": 0, "max": 20}},
            
            # Uric Acid
            "Uric Acid": {"min": 3.5, "max": 7.2, "unit": "mg/dL", "gender_specific": True, "male": {"min": 3.5, "max": 7.2}, "female": {"min": 2.6, "max": 6.0}},
        }
    
    def compare_with_normal_range(self, test_name: str, value: float, gender: Optional[str] = None) -> Dict[str, Any]:
        """Compare a test value with its normal range and return status"""
        if test_name not in self.normal_ranges:
            return {
                "status": "unknown",
                "normal_range": "N/A",
                "change": "N/A",
                "is_abnormal": False
            }
        
        range_info = self.normal_ranges[test_name]
        
        # Handle gender-specific ranges
        if range_info.get("gender_specific") and gender:
            gender_key = gender.lower() if gender else "male"
            if gender_key in ["m", "male"] and "male" in range_info:
                min_val = range_info["male"]["min"]
                max_val = range_info["male"]["max"]
            elif gender_key in ["f", "female"] and "female" in range_info:
                min_val = range_info["female"]["min"]
                max_val = range_info["female"]["max"]
            else:
                min_val = range_info.get("min", 0)
                max_val = range_info.get("max", 1000)
        else:
            min_val = range_info.get("min", 0)
            max_val = range_info.get("max", 1000)
        
        unit = range_info.get("unit", "")
        normal_range_str = f"{min_val}-{max_val} {unit}".strip()
        
        # Determine status
        is_abnormal = False
        status = "Normal"
        change = "→ Stable"
        status_color = "#10b981"
        status_bg = "#d1fae5"
        status_icon = "✅"
        
        if value < min_val:
            is_abnormal = True
            status = "Low"
            change = f"↓ {abs(min_val - value):.1f} {unit}".strip()
            status_color = "#f59e0b"
            status_bg = "#fef3c7"
            status_icon = "⚠️"
        elif value > max_val:
            is_abnormal = True
            status = "High"
            change = f"↑ {abs(value - max_val):.1f} {unit}".strip()
            status_color = "#ef4444"
            status_bg = "#fee2e2"
            status_icon = "🔴"
        
        # For HDL Cholesterol (higher is better)
        if range_info.get("higher_better") and value < min_val:
            is_abnormal = True
            status = "Low"
            change = f"↓ {abs(min_val - value):.1f} {unit}".strip()
            status_color = "#f59e0b"
            status_bg = "#fef3c7"
            status_icon = "⚠️"
        
        return {
            "status": status,
            "normal_range": normal_range_str,
            "change": change,
            "is_abnormal": is_abnormal,
            "status_color": status_color,
            "status_bg": status_bg,
            "status_icon": status_icon,
            "min": min_val,
            "max": max_val
        }
    
    def analyze_measurements(self, measurements: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Analyze measurements and compare with normal ranges"""
        analyzed_measurements = {}
        abnormal_tests = []
        
        for test_name, values in measurements.items():
            if not values or len(values) == 0:
                continue
            
            analyzed_values = []
            for value_dict in values:
                value = value_dict.get("value")
                if value is None:
                    continue
                
                comparison = self.compare_with_normal_range(test_name, value)
                analyzed_value = {
                    **value_dict,
                    **comparison
                }
                analyzed_values.append(analyzed_value)
                
                if comparison["is_abnormal"]:
                    abnormal_tests.append({
                        "test": test_name,
                        "value": value,
                        "unit": value_dict.get("unit", ""),
                        "status": comparison["status"],
                        "normal_range": comparison["normal_range"]
                    })
            
            if analyzed_values:
                analyzed_measurements[test_name] = analyzed_values
        
        return {
            "analyzed_measurements": analyzed_measurements,
            "abnormal_tests": abnormal_tests,
            "total_tests": sum(len(v) for v in measurements.values()),
            "abnormal_count": len(abnormal_tests)
        }
    
    def suggest_diseases_from_measurements(self, abnormal_tests: List[Dict[str, Any]]) -> List[str]:
        """Suggest possible diseases based on abnormal lab values"""
        disease_suggestions = []
        
        for test in abnormal_tests:
            test_name = test["test"].lower()
            status = test["status"].lower()
            value = test["value"]
            
            # Glucose abnormalities
            if "glucose" in test_name:
                if status == "high":
                    disease_suggestions.append("Diabetes")
                elif status == "low":
                    disease_suggestions.append("Hypoglycemia")
            
            # Hemoglobin abnormalities
            if "hemoglobin" in test_name:
                if status == "low":
                    disease_suggestions.append("Anemia")
            
            # Cholesterol abnormalities
            if "cholesterol" in test_name:
                if status == "high" and "total" in test_name:
                    disease_suggestions.append("Hypercholesterolemia")
                if status == "high" and "ldl" in test_name:
                    disease_suggestions.append("Cardiovascular Disease Risk")
            
            # Liver function abnormalities
            if any(x in test_name for x in ["sgpt", "alt", "sgot", "ast", "bilirubin"]):
                if status == "high":
                    disease_suggestions.append("Liver Disease")
            
            # Kidney function abnormalities
            if any(x in test_name for x in ["creatinine", "bun", "urea", "egfr"]):
                if status == "high" or (test_name == "egfr" and status == "low"):
                    disease_suggestions.append("Kidney Disease")
            
            # Thyroid abnormalities
            if "tsh" in test_name:
                if status == "high":
                    disease_suggestions.append("Hypothyroidism")
                elif status == "low":
                    disease_suggestions.append("Hyperthyroidism")
            
            # Vitamin D
            if "vitamin d" in test_name and status == "low":
                disease_suggestions.append("Vitamin D Deficiency")
        
        # Remove duplicates
        return list(set(disease_suggestions))
    
    def _load_drug_interactions(self) -> Dict[str, List[str]]:
        """Load known drug interactions database"""
        return {
            "warfarin": ["aspirin", "ibuprofen", "naproxen", "heparin"],
            "aspirin": ["warfarin", "ibuprofen", "naproxen"],
            "metformin": ["alcohol", "contrast dye"],
            "ace inhibitors": ["potassium supplements", "diuretics"],
            "statins": ["grapefruit", "alcohol"],
        }
    
    def generate_comprehensive_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive summary of the medical report analysis"""
        measurements_analysis = analysis.get("measurements_analysis", {})
        abnormal_count = measurements_analysis.get("abnormal_count", 0)
        total_tests = measurements_analysis.get("total_tests", 0)
        
        summary = {
            "total_diseases": len(analysis.get("diseases", [])),
            "total_medications": len(analysis.get("medications", [])),
            "total_measurements": total_tests or sum(len(v) for v in analysis.get("measurements", {}).values()),
            "total_recommendations": len(analysis.get("recommendations", [])),
            "key_highlights": [],
            "risk_level": "low",
            "summary_text": ""
        }
        
        # Build summary text
        summary_parts = []
        
        # Extract key highlights
        diseases = analysis.get("diseases", [])
        if diseases:
            summary["key_highlights"].append(f"Detected {len(diseases)} medical condition(s): {', '.join(diseases[:3])}")
            summary_parts.append(f"Detected {len(diseases)} medical condition(s): {', '.join(diseases)}")
        
        medications = analysis.get("medications", [])
        if medications:
            med_names = [m.get("name", m) if isinstance(m, dict) else m for m in medications[:3]]
            summary["key_highlights"].append(f"Identified {len(medications)} medication(s): {', '.join(med_names)}")
            summary_parts.append(f"Identified {len(medications)} medication(s)")
        
        # Add lab measurements summary
        if total_tests > 0:
            if abnormal_count > 0:
                summary_parts.append(f"Found {abnormal_count} abnormal lab value(s) out of {total_tests} tests")
                summary["key_highlights"].append(f"{abnormal_count} abnormal lab value(s) detected")
            else:
                summary_parts.append(f"All {total_tests} lab test(s) are within normal range")
        
        summary["summary_text"] = ". ".join(summary_parts) + "." if summary_parts else "Analysis complete."
        
        # Determine risk level based on abnormal tests and diseases
        critical_conditions = ["cancer", "heart attack", "stroke", "sepsis", "tuberculosis"]
        if any(cond.lower() in str(diseases).lower() for cond in critical_conditions):
            summary["risk_level"] = "high"
        elif abnormal_count > 5 or len(diseases) > 3 or len(medications) > 5:
            summary["risk_level"] = "medium"
        elif abnormal_count > 0:
            summary["risk_level"] = "low"
        
        return summary
    
    def generate_priority_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate prioritized recommendations based on analysis"""
        priority_recs = []
        
        diseases = analysis.get("diseases", [])
        medications = analysis.get("medications", [])
        recommendations = analysis.get("recommendations", [])
        measurements_analysis = analysis.get("measurements_analysis", {})
        abnormal_tests = measurements_analysis.get("abnormal_tests", [])
        
        # High priority: Critical conditions
        critical_keywords = ["cancer", "tumor", "malignancy", "heart attack", "stroke", "sepsis"]
        if any(keyword in str(diseases).lower() for keyword in critical_keywords):
            priority_recs.append({
                "priority": 1,
                "title": "Seek Immediate Medical Attention",
                "description": "Critical condition detected. Consult a specialist urgently.",
                "action": "Visit emergency department or contact specialist immediately",
                "category": "Critical Condition",
                "urgency": "high"
            })
        
        # High priority: Multiple abnormal tests
        if len(abnormal_tests) > 5:
            priority_recs.append({
                "priority": 2,
                "title": "Multiple Abnormal Lab Values",
                "description": f"{len(abnormal_tests)} test results are outside normal range. Comprehensive evaluation recommended.",
                "action": "Schedule appointment with primary care physician for complete assessment",
                "category": "Lab Results",
                "urgency": "high"
            })
        
        # Medium priority: Abnormal lab values
        if abnormal_tests:
            critical_abnormal = [t for t in abnormal_tests if t.get("status", "").lower() in ["high", "low"]]
            if critical_abnormal:
                test_names = ", ".join([t["test"] for t in critical_abnormal[:3]])
                priority_recs.append({
                    "priority": 3,
                    "title": "Abnormal Lab Values Detected",
                    "description": f"Following tests are outside normal range: {test_names}",
                    "action": "Consult with your doctor to discuss these results and next steps",
                    "category": "Lab Results",
                    "urgency": "medium"
                })
        
        # Medium priority: Multiple medications
        if len(medications) > 3:
            priority_recs.append({
                "priority": 4,
                "title": "Medication Review Recommended",
                "description": "You are taking multiple medications. Review with healthcare provider.",
                "action": "Schedule medication review with pharmacist or doctor",
                "category": "Medication Management",
                "urgency": "medium"
            })
        
        # Medium priority: Chronic conditions
        chronic_conditions = ["diabetes", "hypertension", "asthma", "copd", "ckd"]
        if any(cond.lower() in str(diseases).lower() for cond in chronic_conditions):
            priority_recs.append({
                "priority": 5,
                "title": "Chronic Disease Management",
                "description": "Regular monitoring and follow-ups are important for chronic conditions.",
                "action": "Schedule regular follow-up appointments with your specialist",
                "category": "Chronic Disease Management",
                "urgency": "medium"
            })
        
        # Low priority: General recommendations
        if recommendations:
            for i, rec in enumerate(recommendations[:3], start=6):
                rec_text = rec if isinstance(rec, str) else str(rec)
                priority_recs.append({
                    "priority": i,
                    "title": "General Health Recommendation",
                    "description": rec_text,
                    "action": "Follow general health guidelines and lifestyle modifications",
                    "category": "General Care",
                    "urgency": "low"
                })
        
        return priority_recs
    
    def check_drug_interactions(self, medications: List[Any]) -> List[Dict[str, str]]:
        """Check for potential drug interactions"""
        interactions = []
        
        if not medications:
            return interactions
        
        # Extract medication names
        med_names = []
        for med in medications:
            if isinstance(med, dict):
                med_names.append(med.get("name", "").lower())
            elif isinstance(med, str):
                med_names.append(med.lower())
        
        # Check for known interactions
        for i, med1 in enumerate(med_names):
            for med2 in med_names[i+1:]:
                # Check direct interactions
                if med1 in self.drug_interactions_db:
                    if any(med2.startswith(interaction) or interaction in med2 
                          for interaction in self.drug_interactions_db[med1]):
                        interactions.append({
                            "medication1": med1,
                            "medication2": med2,
                            "interaction_type": "potential",
                            "severity": "moderate",
                            "recommendation": f"Consult doctor about potential interaction between {med1} and {med2}"
                        })
        
        # Check for common interaction patterns
        if "warfarin" in med_names and any("aspirin" in m or "ibuprofen" in m for m in med_names):
            interactions.append({
                "medication1": "warfarin",
                "medication2": "aspirin/nsaids",
                "interaction_type": "bleeding_risk",
                "severity": "high",
                "recommendation": "Warfarin with NSAIDs increases bleeding risk. Monitor closely."
            })
        
        return interactions

