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
    'name': 'Product Pack',
    "version": '1.0',
    'sequence': 14,
    'category': 'Product',
    "license": 'AGPL-3',
    'summary': 'Product pack management',
    'author': 'Matthieu JOOSSEN',
    'depends': [
        'sale',
        'sales_team',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/pack_view.xml',
        'views/sale_view.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
