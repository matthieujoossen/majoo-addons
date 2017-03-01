# -*- encoding: utf-8 -*-

from odoo import models, _
from odoo.exceptions import UserError


class PosOrder(models.Model):
    _inherit = "pos.order"

    def create_picking(self):
        '''this call will create pickings for normal products'''
        super(PosOrder, self).create_picking()
        ''' Below code will create another picking for packs'''
        picking_obj = self.env['stock.picking']
        partner_obj = self.env['res.partner']
        move_obj = self.env['stock.move']

        for order in self:
            addr = order.partner_id and order.partner_id.address_get(['delivery']) or {}
            picking_type = order.picking_type_id
            picking_id = False
            if picking_type:
                picking_id = picking_obj.create({
                    'origin': order.name,
                    'partner_id': addr.get('delivery', False),
                    'date_done': order.date_order,
                    'picking_type_id': picking_type.id,
                    'company_id': order.company_id.id,
                    'move_type': 'direct',
                    'note': order.note or "",
                    'invoice_state': 'none',
                })
                order.write({'picking_id': picking_id.id})
            location_id = order.location_id.id
            if order.partner_id:
                destination_id = order.partner_id.property_stock_customer.id
            elif picking_type:
                if not picking_type.default_location_dest_id:
                    raise UserError(_("""Missing source or destination location for picking type %s.
Please configure those fields and try again.""" % (picking_type.name,)))
                destination_id = picking_type.default_location_dest_id.id
            else:
                destination_id = partner_obj.default_get(['property_stock_customer'])['property_stock_customer']

            for line in order.lines:
                if line.product_id.pack:
                    for pack_line in line.product_id.pack_line_ids:

                        move_list = self.env['stock..move']
                        move_list += move_obj.create({
                            'name': pack_line.product_id.name,
                            'product_uom': pack_line.product_id.uom_id.id,
                            'product_uos': pack_line.product_id.uom_id.id,
                            'picking_id': picking_id.id,
                            'picking_type_id': picking_type.id,
                            'product_id': pack_line.product_id.id,
                            'product_uos_qty': abs(pack_line.quantity * line.qty),
                            'product_uom_qty': abs(pack_line.quantity * line.qty),
                            'state': 'draft',
                            'location_id': location_id if line.qty >= 0 else destination_id,
                            'location_dest_id': destination_id if line.qty >= 0 else location_id,
                        })

                        if picking_id:
                            picking_id.action_confirm()
                            picking_id.force_assign()
                            picking_id.action_done()
                        elif move_list:
                            move_list.action_confirm()
                            move_list.force_assign()
                            move_list.action_done()
        return True
