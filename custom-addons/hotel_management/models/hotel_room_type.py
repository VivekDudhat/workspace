from odoo import api, fields, models 


class RoomType(models.Model):

    _name= "room.type"
    _description = "Room Type"
    _rec_name = "room_type"
   

    room_type = fields.Char(string = "Room Type")
    room_details = fields.Text(string = "Room Details")
    room_price = fields.Float(string = "Room Price")
    room_image = fields.Image(string='Room Photo')