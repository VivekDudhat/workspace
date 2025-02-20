from odoo import fields, api, models
from odoo.exceptions import ValidationError

class RoomCleaning(models.Model):
    _name = "hotel.room.cleaning"
    _description = "Room Cleaning"
    _rec_name = "cleaning_id"

    cleaning_id = fields.Many2one('hotel.rooms', string='Room Number', required=True)
    cleaning_date = fields.Date(string='Cleaning Date', default=fields.Date.today, required=True)
    charge = fields.Float(string = 'Charge for Room cleaning',default='500', readonly=True)
    total_cost = fields.Float(string='Total Charge', compute='_compute_charge', store=True)
    customer_id = fields.Many2one('hotel.room.booking', string = 'Customer Name')

    @api.depends('cleaning_id', 'cleaning_date')
    def _compute_charge(self):
        for record in self:
            # Skip computation for new records (temporary NewId)
            if not record.id :
                record.total_cost = 0
                continue

            # Count the number of cleanings for the same room on the same day
            cleaning_count = self.search_count([
                ('cleaning_id', '=', record.cleaning_id.id),
                ('cleaning_date', '=', record.cleaning_date),
                ('id', '!=', record.id)  # Exclude the current record
            ])
            
            # If more than one cleaning, charge 500 INR per additional cleaning
            if cleaning_count > 0:
                record.total_cost = 500 * cleaning_count
            else:
                record.total_cost = 0

    @api.model
    def create(self, vals):
        # Ensure that the cleaning date is set to today if not provided
        if 'cleaning_date' not in vals:
            vals['cleaning_date'] = fields.Date.today()
        
        # Create the record
        record = super(RoomCleaning, self).create(vals)
        
        # Recompute the charge for the new record
        record._compute_charge()
        
        return record

    @api.constrains('cleaning_id', 'cleaning_date')
    def _check_cleaning_limit(self):
        for record in self:
            # Skip check for new records (temporary NewId)
            if not record.id :
                continue

            # Count the number of cleanings for the same room on the same day
            cleaning_count = self.search_count([
                ('cleaning_id', '=', record.cleaning_id.id),
                ('cleaning_date', '=', record.cleaning_date),
                ('id', '!=', record.id)  # Exclude the current record
            ])
            
           
           