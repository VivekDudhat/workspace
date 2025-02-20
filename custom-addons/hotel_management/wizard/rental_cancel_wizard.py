from odoo import fields,api,models 




class RentalCancelWizard(models.TransientModel):
    _name = 'rental.cancel.wizard'
    _description = 'Rental Cancel'

    

    reason = fields.Char(string ="Reason for cancelling the booking")

    def action_confirm_cancel(self):
        rental_id = self.env.context.get('active_id')
        rental_record = self.env['hotel.rental'].browse(rental_id)
        if rental_record:
            rental_record.write({'state': 'cancel'})
            rental_record.message_post(body=f"Booking cancelled. Reason: {self.reason}")
    