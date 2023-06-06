# Copyright (c) 2023, Bantoo and contributors
# For license information, please see license.txt

import frappe
from typing import Any, Dict, List, Optional, TypedDict

from frappe import _
import erpnext

class StockLevelsByCategoryFilter(TypedDict):
	company: Optional[str]
	livestock: Optional[str]

def execute(filters: Optional[StockLevelsByCategoryFilter] = None):
	if not filters:
		filters = {}

	if filters.get("company"):
		company_currency = erpnext.get_company_currency(filters.get("company"))
	else:
		company_currency = frappe.db.get_single_value("Global Defaults", "default_currency")

	include_uom = filters.get("include_uom")
	columns = get_columns(filters)
	livestock_data = get_livestock_data(filters)


	# if no entries found return
	if not livestock_data:
		return columns, []

	data = livestock_data
	"""data = []

	for livestock in livestock_data:

		report_data = {
			"warehouse": warehouse,
			"currency": company_currency,
			"item_code": item,
			"company": company,
		}
		report_data.update(item_map[item])

	data.append(report_data)"""

	return columns, data

def get_livestock_data(filters: StockLevelsByCategoryFilter) -> List[str]:
	"Get items based on item code, item group."

	if livestock := filters.get("livestock"):
		livestock = {"livestock": filters.get("livestock")}
	else:
		livestock = {}	
	#frappe.errprint("livestock " + str(livestock))	
	return frappe.get_all(
				"Livestock Balance", 
				order_by="livestock ASC", 
				filters=livestock,  
				fields=[
					"date", "name", "livestock", "current_balance", "last_balance", "last_transaction"
			])


def get_columns(filters: StockLevelsByCategoryFilter):
	"""return columns"""
	
	columns = [

		{
			"label": _("Last Update"),
			"fieldname": "date",
			"fieldtype": "Date",
			"width": 180,
		},
		{
			"label": _("Last Transaction"),
			"fieldname": "last_transaction",
			"fieldtype": "Link",
			"options": "Livestock Entry",
			"width": 200,
		},
		{
			"label": _("Livestock"),
			"fieldname": "livestock",
			"fieldtype": "Link",
			"options": "Livestock",
			"width": 200,
		},
		{
			"label": _("Previous Balance"),
			"fieldname": "last_balance",
			"fieldtype": "Int",
			"width": 200
		},
		{
			"label": _("Current Balance"),
			"fieldname": "current_balance",
			"fieldtype": "Int",
			"width": 200
		}
	]

	return columns
