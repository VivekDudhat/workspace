from odoo import fields, api, models


class HotelResturant(models.Model):
    _name = 'hotel.resturant'
    _description = 'Hotel Restaurant'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'room_id'
     
    room_id = fields.Many2one('hotel.rooms', string="Room", required=True, tracking=True)
    food_id = fields.Many2many(
        'product.product',
        'resturant_product_rel',
        'food_id',
        'product_id',
        string="Food item", required=True, domain=[('categ_id.name', '=', 'Food')]
    )
    food_name = fields.Char(string='Food', tracking = True)
    price = fields.Float(string="Price", related='food_id.lst_price',tracking = True)
    food_image = fields.Binary(string="Food Image", related='food_id.image_1920', store=True)
    total_bill = fields.Float(string="Total Bill", compute='_compute_total_bill', store=True,tracking = True)
    state = fields.Selection([('order', 'Order'), ('cancel', 'Cancel')],)
    customer_id = fields.Many2one('hotel.room.booking', string = 'Customer Name')
    

    @api.depends('food_id')
    def _compute_total_bill(self):
        for record in self:
            record.total_bill = sum(record.food_id.mapped('lst_price'))

    def action_order(self):
        for record in self:
            record.state = 'order'  

    def action_cancel(self):
        for record in self:
            record.state = "cancel"
from odoo import models, fields, api

class HotelResturant(models.Model):
    _name = 'hotel.resturant'
    _description = 'Hotel Restaurant'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'room_id'

    room_id = fields.Many2one('hotel.rooms', string="Room", required=True, tracking=True)
    food_id = fields.Many2many(
        'product.product',
        'resturant_product_rel',
        'food_id',
        'product_id',
        string="Food item", required=True, domain=[('categ_id.name', '=', 'Food')]
    )
    food_name = fields.Char(string='Food', tracking=True)
    price = fields.Float(string="Price", related='food_id.lst_price', tracking=True)
    food_image = fields.Binary(string="Food Image", related='food_id.image_1920', store=True)
    total_bill = fields.Float(string="Total Bill", compute='_compute_total_bill', store=True, tracking=True)
    state = fields.Selection([('order', 'Order'), ('cancel', 'Cancel')], default='order')

    @api.depends('food_id')
    def _compute_total_bill(self):
        for record in self:
            record.total_bill = sum(record.food_id.mapped('lst_price'))

    def action_order(self):
        for record in self:
            record.state = 'order'
            record._post_message()

    def action_cancel(self):
        for record in self:
            record.state = "cancel"
            record._post_message()

    def _post_message(self):
        for record in self:
           food_details = "\n".join([f"- {food.name}: {food.lst_price}" for food in record.food_id])
           total_bill =  f"Total Bill: {record.total_bill}"
           message = f"Food Ordered:\n{food_details}\n{total_bill}"

           record.message_post(
               body=message,
               subtype_xmlid='mail.mt_comment',
               message_type='comment'
           )
