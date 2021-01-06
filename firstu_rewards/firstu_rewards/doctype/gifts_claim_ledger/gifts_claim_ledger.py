# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tridz and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class GiftsClaimLedger(Document):
	def validate(self):
		customer_doc = frappe.get_doc('Customer', self.customer)

		if int(customer_doc.total_trophies_collected) < int(self.trophies_paid):
			self.status = "Failed"
	
		elif int(customer_doc.total_trophies_collected) >= int(self.trophies_paid):	
			self.trophy_ledger_doc = frappe.get_doc({
					'doctype': 'Trophy Ledger',
					'trophy_count': self.trophies_paid,
					'creditdebit': "Debit",
					'customer': self.customer
				})
	def on_submit(self):
		self.trophy_ledger_doc.submit()

		
			
		
			
	