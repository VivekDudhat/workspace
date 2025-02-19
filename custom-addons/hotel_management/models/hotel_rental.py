from odoo import fields,api,models
from datetime import date,datetime



class HotelRental(models.Model):
    _name = "hotel.rental"
    _description = "Rental Service"


    date_of_arrival= fields.Datetime(string = "Date of arrival",required=True)
    pick_up_location = fields.Selection([('airport', 'Airport'),('bus stop','Bus Stop'),('railway station','Railway Station')])
