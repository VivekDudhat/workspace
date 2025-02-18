from odoo import fields, api, models


class HotelResturant(models.Model):
    _name = 'hotel.resturant'
    _description = 'Hotel Resturant'

    
    _inherits = {'product.product': 'food_id'}
    
     
    room_numner_id = fields.Many2one(string='Room Number',comodel_name='hotel.room.booking',ondelete='restrict',)
     
    food_id = fields.Many2one('product.product', string="Food item", required=True, ondelete="cascade",domain=[('categ_id.name','=','Food',)])
    food_name = fields.Char(string='Food')
    price = fields.Float(string = "Price",related='food_id.lst_price')


