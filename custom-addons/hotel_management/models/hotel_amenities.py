from odoo import fields,api,models  


class HotelAmenities(models.Model):
    _name = 'hotel.amenities'
    _description = 'Hotel Amenities'
    _rec_name = "amenity"


    amenity = fields.Char(string = 'Amenity')
    charge = fields.Float(string='Charge')