# -*- encoding: utf-8 -*-

from odoo import fields, models, api
import odoo.addons.decimal_precision as dp


class SaleOrderLinePackLine(models.Model):
    _name = 'sale.order.line.pack.line'
    _description = 'Sale Order None Detailed Pack Lines'

    order_line_id = fields.Many2one('sale.order.line', 'Order Line', ondelete='cascade', required=True)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    currency_id = fields.Many2one('res.currency', related='order_line_id.currency_id')
    price_unit = fields.Monetary('Unit Price', required=True)
    discount = fields.Float('Discount (%)', digits=dp.get_precision('Discount'))
    price_subtotal = fields.Monetary(compute="_amount_line", string='Subtotal')
    product_uom_qty = fields.Float('Quantity', digits=dp.get_precision('Product UoS'), required=True)

    @api.one
    @api.onchange('product_id')
    def onchange_product_id(self):
        self.price_unit = self.product_id.lst_price

    @api.one
    @api.depends('price_unit', 'product_uom_qty')
    def _amount_line(self):
        self.price_subtotal = (self.product_uom_qty * self.price_unit * (1 - (self.discount or 0.0) / 100.0))
