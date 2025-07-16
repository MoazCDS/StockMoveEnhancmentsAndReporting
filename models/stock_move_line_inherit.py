from odoo import models, fields, api

class StockMoveLineInherit(models.Model):
    _inherit = 'stock.move.line'

    move_type = fields.Selection([
        ('scrapped', 'Scrapped'),
        ('internal', 'Internal Transfer'),
        ('purchase', 'Purchase'),
        ('purchase_return', 'Purchase Return'),
        ('sales', 'Sales'),
        ('sales_return', 'Sales Return'),
        ('consignment_in', 'Consignment Receipts'),
        ('consignment_out', 'Consignment Returns'),
        ('manufactured_fp', 'Manufactured Finished Product'),
        ('rm_to_mo', 'Raw Material to Manufacture'),
        ('undefined', 'Undefined'),
    ], compute="_compute_move_type", store=True, string="Move Type")

    current_unit_cost = fields.Float(string='U. Cost', compute='_compute_cost_price_info', store=True)
    current_total_cost = fields.Float(string='T. Cost', compute='_compute_cost_price_info', store=True)

    current_unit_price = fields.Float(string='U. Price', compute='_compute_cost_price_info', store=True)
    current_total_sales = fields.Float(string='T. Price', compute='_compute_cost_price_info', store=True)

    onhand_at_move = fields.Float(string='Onhand', compute='_compute_cost_price_info', store=True)

    @api.depends('location_id', 'location_dest_id', 'owner_id')
    def _compute_move_type(self):
        for rec in self:
            if rec.location_dest_id.scrap_location:
                rec.move_type = 'scrapped'
            elif rec.location_id.usage in ['internal', 'transit'] and rec.location_dest_id.usage in ['internal',
                                                                                                     'transit']:
                rec.move_type = 'internal_transfer'
            elif rec.location_id.usage == 'supplier':
                rec.move_type = 'purchase'
            elif rec.location_dest_id.usage == 'supplier':
                rec.move_type = 'purchase_return'
            elif rec.location_dest_id.usage == 'customer':
                rec.move_type = 'sales'
            elif rec.location_id.usage == 'customer':
                rec.move_type = 'sales_return'
            elif rec.location_id.usage == 'supplier' and rec.owner_id:
                rec.move_type = 'consignment_receipt'
            elif rec.location_dest_id.usage == 'supplier' and rec.owner_id:
                rec.move_type = 'consignment_return'
            elif rec.location_id.usage == 'production':
                rec.move_type = 'manufactured_fp'
            elif rec.location_dest_id.usage == 'production':
                rec.move_type = 'rm_to_manufacture'
            elif (
                    rec.location_id.usage == 'inventory' or rec.location_dest_id.usage == 'inventory') and not rec.location_dest_id.scrap_location:
                rec.move_type = 'inventory_adjustment'
            else:
                rec.move_type = 'undefined'

    @api.depends('product_id', 'date', 'qty_done')
    def _compute_cost_price_info(self):
        for line in self:
            product = line.product_id
            quantity = line.qty_done

            line.current_unit_cost = product.standard_price
            line.current_total_cost = product.standard_price * quantity

            line.current_unit_price = product.lst_price
            line.current_total_sales = product.lst_price * quantity

            move_date = line.date or line.create_date
            line.onhand_at_move = product.with_context(to_date=move_date).qty_available

    def write(self, vals):
        res = super().write(vals)
        if 'state' in vals or 'product_id' in vals or 'date' in vals:
            self._compute_cost_price_info()
        return res