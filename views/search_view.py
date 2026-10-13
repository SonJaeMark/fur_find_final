from views.components.report_browser import ReportBrowser


class SearchView(ReportBrowser):
    def __init__(self, parent, user):
        super().__init__(parent, user, "Unified Search",
                         "Browse and filter all lost and found reports.",
                         manage=user.get_role_name() in ("Admin", "Super Admin"))