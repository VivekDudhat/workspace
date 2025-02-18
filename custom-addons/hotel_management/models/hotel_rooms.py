from odoo import api,fields,models


class HotelRooms(models.Model):

    _name = "hotel.rooms"
    _description = "Hotel Rooms"
    _rec_name = "Rooms"


    Rooms = fields.Char(string='Rooms No.',required=True)
    rooms_ids = fields.Many2one('room.type',string = "Room Type",required=True)
    price = fields.Float(string = 'Price',related='rooms_ids.room_price')
    is_booked = fields.Boolean(string="Booked", default=False)
    
   
  
