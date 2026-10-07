from datetime import datetime
from models.pet_report import PetReport
from utils.matching_engine import MatchingEngine

def test_matching_score_high_match():
    now = datetime.now()
    
    lost = PetReport(
        report_id=1, user_id=10, category="Lost", pet_name="Buddy",
        species="Dog", breed="Golden Retriever", gender="Male",
        primary_color="Golden", secondary_color="White", distinguishing_marks="",
        incident_date=now, location="Manila", photo_path="dummy.jpg"
    )
    
    found = PetReport(
        report_id=2, user_id=11, category="Found", pet_name="Unknown",
        species="Dog", breed="Golden Retriever", gender="Male",
        primary_color="Golden", secondary_color="", distinguishing_marks="",
        incident_date=now, location="Manila", photo_path="dummy.jpg"
    )
    
    score = MatchingEngine.calculate_match_score(lost, found)
    assert score >= 80.0  # High match expected

def test_matching_score_species_mismatch():
    now = datetime.now()
    
    lost = PetReport(
        report_id=1, user_id=10, category="Lost", pet_name="Buddy",
        species="Dog", breed="Labrador", gender="Male",
        primary_color="Black", secondary_color="", distinguishing_marks="",
        incident_date=now, location="Manila", photo_path="dummy.jpg"
    )
    
    found = PetReport(
        report_id=2, user_id=11, category="Found", pet_name="Unknown",
        species="Cat", breed="Persian", gender="Male",
        primary_color="Black", secondary_color="", distinguishing_marks="",
        incident_date=now, location="Manila", photo_path="dummy.jpg"
    )
    
    score = MatchingEngine.calculate_match_score(lost, found)
    assert score == 0.0  # Mismatched species must score 0