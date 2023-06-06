// Copyright (c) 2023, Bantoo and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Livestock Mortality Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "livestock",
			"label": __("Livestock"),
			"fieldtype": "Link",
			"width": "250",
			"options": "Livestock"
		},
		{
			"fieldname": "mortality_reason",
			"label": __("Mortality Reason"),
			"fieldtype": "Link",
			"width": "250",
			"options": "Mortality Reason"
		},
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Company",
			"default": frappe.defaults.get_default("company"),
			"hidden": 1,
		}

	]
};