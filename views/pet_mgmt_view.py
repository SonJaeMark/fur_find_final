from views.components.report_browser import ReportBrowser


class PetMgmtView(ReportBrowser):
    def __init__(self, parent, user):
        super().__init__(parent, user, "Pet Management",
                         "Edit or soft-delete reports. Soft-deleted reports are hidden but kept in the database.",
                         manage=True)