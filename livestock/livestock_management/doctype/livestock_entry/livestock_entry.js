// Copyright (c) 2023, Bantoo and contributors
// For license information, please see license.txt

var livestock_balances = [];
var entry_types = [];

frappe.ui.form.on('Livestock Entry', {
	
	refresh: function(frm) {
		frappe.db.get_list("Livestock Balance", {fields:["livestock", "current_balance"], limit: 0, filters: {company: frm.doc.company}})
		.then(balances => {
			console.table(balances);
			livestock_balances = balances;
		});
		frappe.db.get_list("Livestock Entry Type", {fields:["entry_type", "effect_on_qty"], limit: 0})
		.then(entries => {
			console.table(entries);
			entry_types = entries;
		});
	},
	livestock: function(frm) {
		var balance = getCurrentBalance(livestock_balances, frm.doc.livestock);
		frm.set_value("current_balance", balance);
	},
	quantity: function(frm) {
		let effect_on_qty = getEntryEffect(entry_types, frm.doc.entry_type)
		let balance = 0;

		if (effect_on_qty == 'Increase') {
			balance = frm.doc.current_balance + frm.doc.quantity;
			frm.set_value("balance_after_transaction", balance);
		}
		else if (effect_on_qty == 'Decrease') {
			if (frm.doc.current_balance < frm.doc.quantity) {
				frappe.throw(__("Not enough livestock in stock"));
			}
			balance = frm.doc.current_balance - frm.doc.quantity;
			frm.set_value("balance_after_transaction", balance);
		}
		else {
			balance = frm.doc.current_balance;
		}
	},
});


function getCurrentBalance(array, livestock) {
	for (var i = 0; i < array.length; i++) {
	  if (array[i].livestock === livestock) {
		return array[i].current_balance;
	  }
	}
	return 0; // Return null if livestock is not found
}

function getEntryEffect(array, entry_type) {
	for (var i = 0; i < array.length; i++) {
	  if (array[i].entry_type === entry_type) {
		return array[i].effect_on_qty;
	  }
	}
	return 'Neutral'; // Return neutral if Entry Type is not found
}
