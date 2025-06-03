# -*- coding: utf-8 -*-
{
    'name': "arnian_general",

    'summary': "Modificaciones de arnian generales",

    'description': """
Cotizacion por porcentaje, ajuste en los productos campos de cliente y usuario administrador
modificacion de los porductos para los filtros de entradas no cotizadas, y filtros de entradas por cliente
    """,

    'author': "Daniel Olivares",
    'website': "https://arniangroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.67',

    # any module necessary for this one to work correctly
    'depends': ['base','sale_management','web', 'portal'],

    # always loadeds
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/report_by_date_template.xml',

    ],
    
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}

