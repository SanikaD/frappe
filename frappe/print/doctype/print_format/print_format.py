# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
import frappe.utils
from jinja2 import TemplateSyntaxError

from frappe.model.document import Document

class PrintFormat(Document):
	def validate(self):
		if (self.standard=="Yes"
			and not frappe.local.conf.get("developer_mode")
			and not (frappe.flags.in_import or frappe.flags.in_test)):

			frappe.throw(frappe._("Standard Print Format cannot be updated"))

		# old_doc_type is required for clearing item cache
		self.old_doc_type = frappe.db.get_value('Print Format',
				self.name, 'doc_type')

		if self.html:
			jenv = frappe.get_jenv()
			try:
				jenv.from_string(self.html)
			except TemplateSyntaxError, e:
				frappe.msgprint('Line {}: {}'.format(e.lineno, e.message))
				frappe.throw(frappe._("Syntax error in Jinja template"))

	def on_update(self):
		if hasattr(self, 'old_doc_type') and self.old_doc_type:
			frappe.clear_cache(doctype=self.old_doc_type)
		if self.doc_type:
			frappe.clear_cache(doctype=self.doc_type)

		self.export_doc()

	def export_doc(self):
		# export
		if self.standard == 'Yes' and (frappe.conf.get('developer_mode') or 0) == 1:
			module = frappe.db.get_value("DocType", self.doc_type, "module")
			from frappe.modules.export_file import export_to_files
			export_to_files(record_list=[['Print Format', self.name]],
				record_module= module)

	def on_trash(self):
		if self.doc_type:
			frappe.clear_cache(doctype=self.doc_type)
