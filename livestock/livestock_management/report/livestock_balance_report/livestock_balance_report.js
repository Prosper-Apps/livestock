// Copyright (c) 2023, Bantoo and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Livestock Balance Report"] = {
	"filters": [
		{
			"fieldname": "livestock",
			"label": __("Livestock"),
			"fieldtype": "Link",
			"width": "250",
			"options": "Livestock"
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
