# Copyright (c) 2023, Bantoo and contributors
# For license information, please see license.txt

import frappe
from typing import Any, Dict, List, Optional, TypedDict
from frappe.query_builder.functions import Sum

from frappe import _
import erpnext

class LivestockMortalityFilter(TypedDict):
	company: Optional[str]
	livestock: Optional[str]

LivestockEntry = Dict[str, Any]

def execute(filters: Optional[LivestockMortalityFilter] = None):
	if not filters:
		filters = {}

	if filters.get("company"):
		company_currency = erpnext.get_company_currency(filters.get("company"))
	else:
		company_currency = frappe.db.get_single_value("Global Defaults", "default_currency")

	columns = get_columns(filters)
	data = get_data(filters)


	# if no entries found return
	if not data:
		return columns, []

	return columns, data

def get_data(filters: LivestockMortalityFilter) -> List[LivestockEntry]:
	le = frappe.qb.DocType("Livestock Entry")

	query = (
		frappe.qb.from_(le)
		.select(
			le.name,
			le.date,
			le.livestock,
			Sum(le.quantity).as_("quantity"),
			le.value,
			le.mortality_reason,
			le.disease,
			le.comment
		)
		.where((le.docstatus == 1) & (le.entry_type == 'Mortality'))
		.groupby(le.mortality_reason, le.date)
		.orderby(le.date)
		.orderby(le.livestock)
	)

	query = apply_conditions(query, filters)
	return query.run(as_dict=True)


def apply_conditions(query, filters):
	sle = frappe.qb.DocType("Livestock Entry")

	if from_date := filters.get("from_date"):
		query = query.where(sle.date >= from_date)
	else:
		frappe.throw(_("'From Date' is required"))

	if to_date := filters.get("to_date"):
		query = query.where(sle.date <= to_date)
	else:
		frappe.throw(_("'To Date' is required"))

	if livestock := filters.get("livestock"):
		query = query.where(sle.livestock == livestock)

	if mortality_reason := filters.get("mortality_reason"):
		query = query.where(sle.mortality_reason == mortality_reason)

	if company := filters.get("company"):
		query = query.where(sle.company == company)

	return query

def get_columns(filters: LivestockMortalityFilter):
	"""return columns"""
	
	columns = [

		{
			"label": _("Date"),
			"fieldname": "date",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"label": _("Livestock"),
			"fieldname": "livestock",
			"fieldtype": "Link",
			"options": "Livestock",
			"width": 150,
		},
		{
			"label": _("Quantity"),
			"fieldname": "quantity",
			"fieldtype": "Int",
			"width": 80
		},
		{
			"label": _("Reason"),
			"fieldname": "mortality_reason",
			"fieldtype": "Link",
			"options": "Mortality Reason",
			"width": 200
		},
		{
			"label": _("Disease"),
			"fieldname": "disease",
			"fieldtype": "data",
			"width": 200
		},
		{
			"label": _("Comment"),
			"fieldname": "comment",
			"fieldtype": "data",
			"width": 350
		}
	]
	# suggest code to add column at second to last position if reason == 'Disease'





	return columns
