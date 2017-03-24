# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Creative Commons CC-BY 2017 Matthieu JOOSSEN
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Project Team Worker',
    'version': '1.0',
    'sequence': 140,
    'category': 'Tools',
    'category': 'Point of Sale',
    'license': 'AGPL-3',
    'summary': 'Use teams workers to manage project access',
    'author': 'Matthieu JOOSSEN',
    'depends': [
        'project',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir.rule.csv',
        'views/project_view.xml',
        'views/menu.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
