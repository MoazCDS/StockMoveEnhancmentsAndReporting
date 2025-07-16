from odoo import models, fields, api

class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    current_unit_cost = fields.Float(string='U. Cost', compute='_compute_cost_price_info', store=True)
    current_total_cost = fields.Float(string='T. Cost', compute='_compute_cost_price_info', store=True)

    current_unit_price = fields.Float(string='U. Price', compute='_compute_cost_price_info', store=True)
    current_total_sales = fields.Float(string='T. Price', compute='_compute_cost_price_info', store=True)

    onhand_at_move = fields.Float(string='Onhand', compute='_compute_cost_price_info', store=True)

    @api.depends('stock_move_id.product_id', 'stock_move_id.date', 'stock_move_id.product_uom_qty')
    def _compute_cost_price_info(self):
        for line in self:
            move = line.stock_move_id
            product = move.product_id
            quantity = move.product_uom_qty

            line.current_unit_cost = product.standard_price
            line.current_total_cost = product.standard_price * quantity

            line.current_unit_price = product.lst_price
            line.current_total_sales = product.lst_price * quantity

            move_date = move.date or move.create_date
            line.onhand_at_move = product.with_context(to_date=move_date).qty_available