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
    'name': 'Product Pack POS',
    'version': '1.0',
    'sequence': 50,
    'category': 'Point of Sale',
    'license': 'AGPL-3',
    'summary': 'Product packs on POS',
    'author': 'Matthieu JOOSSEN',
    'depends': [
        'product_pack',
        'point_of_sale'],
    'data': [],
    'demo': [],
    'installable': True,
    'auto_install': True,
    'application': False,
}
