import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime
from datetime import datetime

class LivestockEntry(Document):
    def on_submit(self):
        # Check if this is the first Livestock Entry for the user's company
        existing_balance = frappe.get_all(
            "Livestock Balance",
            filters={"company": self.company, "livestock": self.livestock},
            fields=["name"],
            limit=1,
        )

        if not existing_balance:
            if self.entry_type != "Stock Take":
                frappe.throw(_("You need to enter the first <strong>Stock Take</strong> entry for <strong>{0}</strong>.").format(self.livestock))

            # Create initial Livestock Balance entry for Stock Take
            livestock_balance = frappe.new_doc("Livestock Balance")
            livestock_balance.company = self.company
            livestock_balance.livestock = self.livestock
            livestock_balance.current_balance = self.quantity
            livestock_balance.last_balance = 0
            livestock_balance.last_transaction = self.name
            livestock_balance.insert(ignore_permissions=True)
            frappe.errprint("Created initial Livestock Balance entry for Stock Take")
        else:
            livestock_balance = frappe.get_doc("Livestock Balance", existing_balance[0].name)
            last_balance = livestock_balance.current_balance

            if get_datetime(self.date) < get_datetime(livestock_balance.date):
                livestock_balance.current_balance = self.recalculate_balance(last_balance)
                frappe.errprint("Recalculated Livestock Balance")

            else:
                frappe.errprint("Didnt Recalculate")
                if self.entry_type == "Stock Take":
                    # Update Livestock Balance for Stock Take
                    livestock_balance.current_balance = self.quantity
                    frappe.errprint("Updated Livestock Balance for Stock Take")
                else:
                    effect_on_qty = frappe.get_value("Livestock Entry Type", self.entry_type, "effect_on_qty")
                    if effect_on_qty == "Increase":
                        # Update Livestock Balance for Increase
                        livestock_balance.current_balance = last_balance + self.quantity
                        frappe.errprint("Updated Livestock Balance for Increase")
                    elif effect_on_qty == "Decrease":
                        # Update Livestock Balance for Decrease
                        livestock_balance.current_balance = last_balance - self.quantity
                        frappe.errprint("Updated Livestock Balance for Decrease")

            livestock_balance.last_balance = last_balance
            livestock_balance.last_transaction = self.name
            livestock_balance.save(ignore_permissions=True)
            frappe.errprint("Updated Livestock Balance document")

    def on_cancel(self):
        existing_balance = frappe.get_all(
            "Livestock Balance",
            filters={"company": self.company, "livestock": self.livestock},
            fields=["name"],
            limit=1,
        )
        livestock_balance = frappe.get_doc("Livestock Balance", existing_balance[0].name)
        last_balance = livestock_balance.current_balance
        livestock_balance.current_balance = self.recalculate_balance(last_balance)
        livestock_balance.last_balance = last_balance
        livestock_balance.save(ignore_permissions=True)
        frappe.errprint("Cancelled Livestock Entry and updated Livestock Balance")

    def recalculate_balance(self, last_balance):
        # Adjust the balances starting from the previous stock take
        previous_stock_take = frappe.get_all(
            "Livestock Entry",
            filters={
                "company": self.company,
                "livestock": self.livestock,
                "entry_type": "Stock Take",
                "date": ("<=", self.date),
                "docstatus": 1,
            },
            fields=["date", "quantity", "entry_type"],
            order_by="date DESC",
            limit=1,
        )
        frappe.errprint(previous_stock_take)

        if previous_stock_take:
            last_balance = previous_stock_take[0].quantity

        # Adjust the balances for subsequent entries
        stock_entries = frappe.get_all(
            "Livestock Entry",
            filters={
                "company": self.company,
                "livestock": self.livestock,
                "date": (">=", previous_stock_take[0].date),
                "docstatus": 1,
            },
            fields=["name", "quantity", "entry_type"],
            order_by="date",
            limit=0
        )

        frappe.errprint(stock_entries)

        for entry in stock_entries:
            if entry.entry_type == "Stock Take":
                last_balance = entry.quantity
                frappe.errprint("Found Stock Take entry")
                continue

            effect_on_qty = frappe.get_value("Livestock Entry Type", entry.entry_type, "effect_on_qty")
            if effect_on_qty == "Increase":
                last_balance += entry.quantity
                frappe.errprint("Adjusted balance for Increase")
            elif effect_on_qty == "Decrease":
                last_balance -= entry.quantity
                frappe.errprint("Adjusted balance for Decrease")

        return last_balance
