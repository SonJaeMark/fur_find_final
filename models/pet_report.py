from datetime import datetime
from typing import Optional

class PetReport:
    """Data model representing a lost or found pet report."""

    def __init__(
        self,
        report_id: Optional[int],
        user_id: int,
        category: str,  # 'Lost' or 'Found'
        pet_name: Optional[str],
        species: str,
        breed: str,
        gender: str,
        primary_color: str,
        secondary_color: Optional[str],
        distinguishing_marks: Optional[str],
        incident_date: datetime,
        location: str,
        photo_path: str,
        status: str = "Open"  # 'Open', 'Under Verification', 'Resolved', 'Closed'
    ):
        self.report_id = report_id
        self.user_id = user_id
        self.category = category
        self.pet_name = pet_name or "Unknown"
        self.species = species
        self.breed = breed
        self.gender = gender
        self.primary_color = primary_color
        self.secondary_color = secondary_color or ""
        self.distinguishing_marks = distinguishing_marks or ""
        self.incident_date = incident_date
        self.location = location
        self.photo_path = photo_path
        self.status = status

    def to_dict(self) -> dict:
        """Converts object attributes into a dictionary structure."""
        return {
            "report_id": self.report_id,
            "user_id": self.user_id,
            "category": self.category,
            "pet_name": self.pet_name,
            "species": self.species,
            "breed": self.breed,
            "gender": self.gender,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            "distinguishing_marks": self.distinguishing_marks,
            "incident_date": self.incident_date,
            "location": self.location,
            "photo_path": self.photo_path,
            "status": self.status
        }