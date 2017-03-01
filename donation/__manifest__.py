# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Creative Commons CC-BY 2017 Matthieu JOOSSEN
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Donation',
    'version': '1.0',
    'sequence': 140,
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Manage donations',
    'author': 'Matthieu JOOSSEN',
    'depends': [
        'account_accountant',
    ],
    'data': [
        # security
        'security/donation_security.xml',
        'security/ir.model.access.csv',
        # views
        'views/donation_view.xml',
        'views/account_view.xml',
        'views/product_view.xml',
        'views/donation_campaign_view.xml',
        'views/users_view.xml',
        'views/partner_view.xml',
        'views/donation_report_view.xml',
        'views/donation_validate_view.xml',
        'views/menu.xml',
        # data
        'data/product.category.csv',
        'data/product.template.csv',
        ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
