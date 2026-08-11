{
    'name': "Merge Duplicate Contacts | Duplicate Contacts | Contact Deduplication | Contact Merge | Duplicate Contact Management | Address Book Cleanup | Contact Management",
    'version': '17.0.1.0.0',
    'category': 'CRM',
    'summary': 'Identify and merge duplicate contacts sharing the same name, type, and email with a single click',
    'description': """
Merge Duplicate Contacts (Partners)
==================================
This module helps in database cleaning by identifying duplicate partner records and merging them.
* Centralized "Duplicate Contacts" menu under Contacts app.
* User-friendly list view showing name, email, contact type, duplicate count, and original IDs.
* Details button to view list of all original duplicate contact records.
* Bulk merge operation via the action menu.
* Safe merging using Odoo standard partner merge wizard utilities.
""",
    'website': 'https://uncannycs.com',
    'author': 'Uncanny Consulting Services LLP',
    'maintainer': 'Uncanny Consulting Services LLP',
    'license': 'Other proprietary',
    'depends': ['base', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_duplicate_views.xml',
    ],
    'installable': True,
    'application': True,
    "images": ['static/description/banner.gif'],
    "price": 10,
    "currency": "USD"
}
