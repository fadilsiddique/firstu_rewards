# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tridz and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class GiftsClaimLedger(Document):
	def validate(self):
		self.customer_doc = frappe.get_doc('Customer', self.customer)

		# validate number of trophies customer have against trophies paid for the gift claim. Each gifts are claimed at the cost of trophies needed for the gift.
		# gift claim fails when customer does not have required number of trophies.
		# No. of trophies are deducted upon usage of trophies for gift claim.

		if int(self.customer_doc.total_trophies_collected) < int(self.trophies_paid):
			self.status = 'Failed' # gift claim fails if number of trophy requirment is not met
			self.trophy_ledger_doc = frappe.get_doc({
					'doctype': 'Trophy Ledger',
					'trophy_count': self.trophies_paid,
					'creditdebit': "Debit",
					'note': 'Gift Claim Failed',
					'customer': self.customer,
					'status': 'Failed'
				})
			
	
		elif int(self.customer_doc.total_trophies_collected) >= int(self.trophies_paid):	
			self.trophy_ledger_doc = frappe.get_doc({
					'doctype': 'Trophy Ledger',
					'trophy_count': self.trophies_paid,
					'creditdebit': "Debit",
					'note': 'Gift Claimed',
					'customer': self.customer
				})
			self.customer_doc.total_trophies_collected = int(self.customer_doc.total_trophies_collected) - int(self.trophies_paid) # No. of trophies get deducted upon usage of trophies
	def on_submit(self):
		self.trophy_ledger_doc.submit()
		self.customer_doc.save()

		
			
		
			
	