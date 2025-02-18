from odoo import fields, api, models


class HotelResturant(models.Model):
    _name = 'hotel.resturant'
    _description = 'Hotel Resturant'

    
    _inherits = {'product.product': 'food_id'}
    room_id = fields.Many2one('hotel.rooms', string="Room", required=True,tracking = True)
    food_id = fields.Many2one('product.product', string="Food item", required=True, ondelete="cascade",domain=[('categ_id.name','=','Food',)])
    food_name = fields.Char(string='Food')
    price = fields.Float(string = "Price",related='food_id.lst_price')
    state = fields.Selection([('order', 'Order'),('cancel','Cancel')])





    def action_order(self):
        for records in self:
            records.state == 'order'

    def action_cancel(self):
        for records in self:
            records.state == "cancel"