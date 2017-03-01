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
    'name': 'Account Check Deposit',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Manage deposit of checks to the bank',
    "author": 'Matthieu JOOSSEN',
    'depends': [
        'account_accountant',
        'report',
    ],
    'data': [
        # security
        'security/ir.model.access.csv',
        'security/check_deposit_security.xml',
        # data
        'data/account_data.xml',
        'data/account_deposit_sequence.xml',
        # views
        'views/account_deposit_view.xml',
        'views/account_move_line_view.xml',
        'views/company_view.xml',
        # report
        'report/report.xml',
        'report/report_checkdeposit.xml',
    ],
    'installable': True,
    'application': True,
}
