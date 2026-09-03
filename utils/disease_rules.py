# Disease to Specialization Rule Engine

DEFAULT_DISEASE_MAPPINGS = {
    "Heart problem": "Cardiologist",
    "Cardiovascular / Chest pain": "Cardiologist",
    "Skin problem / Rash / Acne": "Dermatologist",
    "Brain / Nerves / Migraine": "Neurologist",
    "Bone / Joint problem / Back pain": "Orthopedic",
    "Child health / Pediatrics": "Pediatrician",
    "Pregnancy / Women's health": "Gynecologist",
    "Ear / Nose / Throat": "ENT Specialist",
    "Dental / Tooth problem": "Dentist",
    "Eye / Vision problem": "Ophthalmologist",
    "Mental health / Anxiety / Stress": "Psychiatrist",
    "Fever / Common cold / General illness": "General Physician"
}

DISCLAIMER_TEXT = "⚠️ **Disclaimer**: This system provides basic department guidance based on general rules only and does not provide formal medical diagnosis. In case of an emergency, please visit the emergency room immediately."

def get_specialization_for_problem(problem_text: str) -> str:
    """Returns the recommended doctor specialization based on keyword matching."""
    if not problem_text:
        return "General Physician"
    
    problem_lower = problem_text.lower()
    
    keywords = {
        "heart": "Cardiologist",
        "cardio": "Cardiologist",
        "chest pain": "Cardiologist",
        "skin": "Dermatologist",
        "rash": "Dermatologist",
        "acne": "Dermatologist",
        "derma": "Dermatologist",
        "brain": "Neurologist",
        "nerve": "Neurologist",
        "migraine": "Neurologist",
        "seizure": "Neurologist",
        "headache": "Neurologist",
        "bone": "Orthopedic",
        "joint": "Orthopedic",
        "fracture": "Orthopedic",
        "spine": "Orthopedic",
        "ortho": "Orthopedic",
        "child": "Pediatrician",
        "baby": "Pediatrician",
        "infant": "Pediatrician",
        "pediatric": "Pediatrician",
        "pregnancy": "Gynecologist",
        "women": "Gynecologist",
        "gyn": "Gynecologist",
        "ear": "ENT Specialist",
        "nose": "ENT Specialist",
        "throat": "ENT Specialist",
        "sinus": "ENT Specialist",
        "ent": "ENT Specialist",
        "teeth": "Dentist",
        "tooth": "Dentist",
        "dental": "Dentist",
        "eye": "Ophthalmologist",
        "vision": "Ophthalmologist",
        "cataract": "Ophthalmologist",
        "mental": "Psychiatrist",
        "anxiety": "Psychiatrist",
        "depression": "Psychiatrist",
        "stress": "Psychiatrist",
        "psych": "Psychiatrist",
        "fever": "General Physician",
        "cold": "General Physician",
        "flu": "General Physician",
        "cough": "General Physician"
    }

    for key, spec in keywords.items():
        if key in problem_lower:
            return spec

    return "General Physician"
