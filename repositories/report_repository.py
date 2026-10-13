from typing import Optional, List, Dict, Any
from repositories.base_repository import BaseRepository
from models.pet_report import PetReport

class ReportRepository(BaseRepository):
    """Data Access Object for tbl_reports (Lost and Found pet reports)."""
    EDITABLE = ("pet_name", "species", "breed", "gender", "primary_color",
                "secondary_color", "distinguishing_marks", "location", "status")

    @staticmethod
    def row_to_report(r: Dict[str, Any]) -> PetReport:
        return PetReport(
            report_id=r["report_id"], user_id=r["user_id"], category=r["report_type"],
            pet_name=r.get("pet_name"), species=r["species"],
            breed=r.get("breed") or "Unknown", gender=r.get("gender") or "Unknown",
            primary_color=r.get("primary_color") or "", secondary_color=r.get("secondary_color"),
            distinguishing_marks=r.get("distinguishing_marks"), incident_date=r["incident_date"],
            location=r["location"], photo_path=r.get("photo_path") or "",
            status=r.get("status") or "Active")

    def get_reports_by_category(self, category: str, status: Optional[str] = None) -> List[PetReport]:
        rows = self.search_reports(report_type=category, status=status)
        return [self.row_to_report(r) for r in rows]

    def get_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        q = "SELECT * FROM tbl_reports WHERE user_id = %s AND is_deleted = 0 ORDER BY report_id DESC"
        return self.execute_query(q, (user_id,), fetch_all=True)

    def update_report(self, report_id: int, data: Dict[str, Any]) -> bool:
        cols = [c for c in self.EDITABLE if c in data]
        if not cols:
            return False
        q = f"UPDATE tbl_reports SET {', '.join(c + ' = %s' for c in cols)} WHERE report_id = %s"
        self.execute_query(q, tuple(data[c] for c in cols) + (report_id,), commit=True)
        return True

    def update_report_status(self, report_id: int, status: str) -> bool:
        return self.update_status(report_id, status)
    def create_report(self, report_data: Dict[str, Any]) -> int:
        query = """
            INSERT INTO tbl_reports 
            (user_id, report_type, pet_name, species, breed, gender, primary_color, 
             secondary_color, distinguishing_marks, incident_date, location, photo_path, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            report_data["user_id"],
            report_data["report_type"], # 'Lost' or 'Found'
            report_data.get("pet_name"),
            report_data["species"],
            report_data.get("breed"),
            report_data.get("gender"),
            report_data.get("primary_color"),
            report_data.get("secondary_color"),
            report_data.get("distinguishing_marks"),
            report_data["incident_date"],
            report_data["location"],
            report_data.get("photo_path"),
            report_data.get("status", "Open")
        )
        return self.execute_query(query, params, commit=True)

    def get_by_id(self, report_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM tbl_reports WHERE report_id = %s AND is_deleted = 0"
        return self.execute_query(query, (report_id,), fetch_one=True)

    def search_reports(self, species: Optional[str] = None, report_type: Optional[str] = None, 
                       status: Optional[str] = None, keyword: Optional[str] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM tbl_reports WHERE is_deleted = 0"
        params = []

        if species:
            query += " AND species = %s"
            params.append(species)
        if report_type:
            query += " AND report_type = %s"
            params.append(report_type)
        if status:
            query += " AND status = %s"
            params.append(status)
        if keyword:
            query += " AND (pet_name LIKE %s OR location LIKE %s OR distinguishing_marks LIKE %s)"
            kw = f"%{keyword}%"
            params.extend([kw, kw, kw])

        return self.execute_query(query, tuple(params), fetch_all=True)

    def update_status(self, report_id: int, status: str) -> bool:
        query = "UPDATE tbl_reports SET status = %s WHERE report_id = %s"
        self.execute_query(query, (status, report_id), commit=True)
        return True

    def soft_delete(self, report_id: int) -> bool:
        query = "UPDATE tbl_reports SET is_deleted = 1 WHERE report_id = %s"
        self.execute_query(query, (report_id,), commit=True)
        return True