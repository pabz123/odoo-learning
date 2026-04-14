{
    "name": "Library Training",
    "version": "1.0.0",
    "summary": "Practice module for Topics 1-7",
    "depends": ["base", "mail"],
    "data": [
        "security/library_security.xml",
        "security/ir.model.access.csv",
        "views/library_book_views.xml",
        "views/library_borrowing_views.xml",
        "views/library_menus.xml",
    ],
    "installable": True,
    "application": True,
}
