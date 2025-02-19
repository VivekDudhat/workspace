# -*- coding: utf-8 -*-
{
    'name': "Hotel_Management",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['web','mail','product'],

    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "views/views.xml",
        "views/templates.xml",
        "views/hotel_rooms_views.xml",
        "views/hotel_resturant_views.xml",
        "views/hotel_main_views.xml",
        "views/room_type_views.xml",
        "views/hotel_room_booking_views.xml",
        "views/hotel_room_cleaning_views.xml",
        "views/hotel_rental_views.xml"
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

