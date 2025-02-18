from odoo import fields,api,models  




class RoomCleaning(models.Model):
    _name = "hotel.room.cleaning"
    _desctiption = "Room Cleaning"

    cleaning_id = fields.Many2one('hotel.rooms',string='Room Number',)