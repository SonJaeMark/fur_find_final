from datetime import datetime
from models.pet_report import PetReport

class MatchingEngine:
    """Algorithmic engine for comparing lost and found reports with weighted scoring."""

    # Scoring Weights (Totaling 1.0 or 100%)
    WEIGHT_SPECIES = 0.30       # Hard constraint requirement
    WEIGHT_GENDER = 0.15
    WEIGHT_BREED = 0.20
    WEIGHT_COLOR = 0.15
    WEIGHT_LOCATION = 0.10
    WEIGHT_DATE_PROXIMITY = 0.10

    @classmethod
    def calculate_match_score(cls, lost_report: PetReport, found_report: PetReport) -> float:
        """Calculates a overall match confidence score (0.0 to 100.0) between two reports."""
        
        # Rule 1: Species must match. If species differs, total score is 0.
        if lost_report.species.lower() != found_report.species.lower():
            return 0.0

        score = cls.WEIGHT_SPECIES * 100.0

        # Gender Comparison
        if lost_report.gender.lower() == found_report.gender.lower() or "unknown" in (lost_report.gender.lower(), found_report.gender.lower()):
            score += cls.WEIGHT_GENDER * 100.0

        # Breed Comparison
        if lost_report.breed.lower() == found_report.breed.lower():
            score += cls.WEIGHT_BREED * 100.0
        elif lost_report.breed.lower() in found_report.breed.lower() or found_report.breed.lower() in lost_report.breed.lower():
            score += (cls.WEIGHT_BREED * 0.5) * 100.0

        # Color Match
        if lost_report.primary_color.lower() == found_report.primary_color.lower():
            score += cls.WEIGHT_COLOR * 100.0
        elif lost_report.primary_color.lower() in found_report.secondary_color.lower() or found_report.primary_color.lower() in lost_report.secondary_color.lower():
            score += (cls.WEIGHT_COLOR * 0.5) * 100.0

        # Location Match
        if lost_report.location.lower() == found_report.location.lower():
            score += cls.WEIGHT_LOCATION * 100.0
        elif lost_report.location.lower() in found_report.location.lower() or found_report.location.lower() in lost_report.location.lower():
            score += (cls.WEIGHT_LOCATION * 0.5) * 100.0

        # Date Proximity Scoring
        days_diff = abs((lost_report.incident_date - found_report.incident_date).days)
        if days_diff <= 1:
            score += cls.WEIGHT_DATE_PROXIMITY * 100.0
        elif days_diff <= 7:
            score += (cls.WEIGHT_DATE_PROXIMITY * 0.7) * 100.0
        elif days_diff <= 30:
            score += (cls.WEIGHT_DATE_PROXIMITY * 0.3) * 100.0

        return round(score, 2)