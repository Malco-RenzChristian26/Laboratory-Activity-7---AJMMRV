import math
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

# COLORS / FONTS
BG = "#000000"
PANEL_BG = "#0b0b0b"
PANEL_BORDER = "#2a2a2a"
HEADER_BG = "#972828"
ENTRY_BG = "#0b0b0b"
FG = "#F2F2F2"
FG_MUTED = "#b5b5b5"
GREEN = "#2ecc71"
RED = "#ff5c5c"
BLUE = "#E45742"


FONT = "Segoe UI"
F_TITLE = (FONT, 16, "bold")
F_SUB = (FONT, 9)
F_HEAD = (FONT, 12, "bold")
F_LABEL = (FONT, 10, "bold")
F_MSG = (FONT, 9)
F_ENTRY = (FONT, 10)
F_TEXT = ("Consolas", 10)

PESO = "\u20b1"


# MAIN WINDOW
root = tk.Tk()
root.title("Robust Inventory Form")
root.geometry("980x700")
root.minsize(900, 640)
root.configure(bg=BG)

# STRINGVARS
name_var = tk.StringVar()
quantity_var = tk.StringVar()
price_var = tk.StringVar()

record_count = 0 



# SMALL UI HELPERS

def make_panel(parent):
    """A bordered dark panel (tk.Frame)."""
    return tk.Frame(
        parent,
        bg=PANEL_BG,
        highlightbackground=PANEL_BORDER,
        highlightthickness=1,
        padx=10,
        pady=8,
    )


def set_message(label, text, ok):
    """Show a validation message in green (valid) or red (error)."""
    label.config(text=text, fg=GREEN if ok else RED)



# VALIDATION TRACE LOG
def log_trace(test_input, expected, actual):
    """Append one line to the Validation Trace Log area."""
    stamp = datetime.now().strftime("%H:%M:%S")
    trace_text.config(state="normal")
    trace_text.insert(
        "end", f"[{stamp}] {test_input} | {expected} | {actual}\n"
    )
    trace_text.see("end")
    trace_text.config(state="disabled")


# TASK 2 / 3 - VALIDATION FUNCTION

def check_name(raw):
    text = raw.strip()
    if text == "":
        return False, None, "Product name must not be empty."
    return True, text, "Valid product name."


def check_quantity(raw):
    text = raw.strip()
    if text == "":
        return False, None, "Quantity is required."
    try:
        if "_" in text: # int("1_0") would wrongly be accepted in Python
            raise ValueError("underscore not allowed")
        quantity = int(text) # rejects 5.5 and abc by raising ValueError
    except ValueError:
        return False, None, "Quantity must be a whole number (e.g. 10)."
    if quantity <= 0:
        return False, None, "Quantity must be greater than zero."
    return True, quantity, "Valid quantity."


def check_price(raw):
    text = raw.strip().replace(",", "")
    if text == "":
        return False, None, "Unit price is required."
    try:
        # only digits, one optional leading sign and decimal point allowed
        if not set(text) <= set("0123456789.+-"):
            raise ValueError("invalid characters")
        price = float(text) # rejects hello
        if not math.isfinite(price):
            raise ValueError("not finite")
    except ValueError:
        return False, None, "Unit price must be a valid number (e.g. 250.00)."
    if price <= 0:
        return False, None, "Unit price must be greater than zero."
    return True, price, "Valid unit price."



# REAL-TIME VALIDATION CALLBACKS


def validate_name(*args):
    ok, _, msg = check_name(name_var.get())
    set_message(name_msg, msg, ok)
    update_status()


def validate_quantity(*args):
    ok, _, msg = check_quantity(quantity_var.get())
    set_message(quantity_msg, msg, ok)
    update_status()


def validate_price(*args):
    ok, _, msg = check_price(price_var.get())
    set_message(price_msg, msg, ok)
    update_status()


def update_status(*args):
    """Overall form status shown in the Validation Messages panel."""
    n_ok = check_name(name_var.get())[0]
    q_ok = check_quantity(quantity_var.get())[0]
    p_ok = check_price(price_var.get())[0]

    if n_ok and q_ok and p_ok:
        status_label.config(
            text="Form is valid. You may click Submit Product.", fg=GREEN
        )
        return

    problems = []
    if not n_ok:
        problems.append("Product Name")
    if not q_ok:
        problems.append("Quantity")
    if not p_ok:
        problems.append("Unit Price")
    status_label.config(
        text="Please fix: " + ", ".join(problems) + ".", fg=RED
    )


# LOG

def log_field_name(event=None):
    raw = name_var.get()
    ok, _, msg = check_name(raw)
    label = "Product name: (empty)" if raw.strip() == "" else f"Product name: {raw}"
    expected = "Accepted" if ok else "Error displayed"
    log_trace(label, expected, msg)


def log_field_quantity(event=None):
    raw = quantity_var.get()
    ok, _, msg = check_quantity(raw)
    label = f"Quantity: {raw if raw.strip() else '(empty)'}"
    expected = "Accepted" if ok else "Rejected"
    log_trace(label, expected, msg)


def log_field_price(event=None):
    raw = price_var.get()
    ok, _, msg = check_price(raw)
    label = f"Unit price: {raw if raw.strip() else '(empty)'}"
    expected = "Accepted" if ok else "Rejected"
    log_trace(label, expected, msg)



# TASK 3 - SUBMIT PRODUCT
def submit_product():
    """Validate again (real-time validation alone is not enough) then add."""
    global record_count

    raw_name = name_var.get()
    raw_qty = quantity_var.get()
    raw_price = price_var.get()
    summary = f"Submit: {raw_name or '(empty)'} / {raw_qty or '(empty)'} / {raw_price or '(empty)'}"

    name_ok, name, name_m = check_name(raw_name)
    qty_ok, quantity, qty_m = check_quantity(raw_qty)
    price_ok, price, price_m = check_price(raw_price)

    errors = []
    if not name_ok:
        errors.append(f"Product Name: {name_m}")
    if not qty_ok:
        errors.append(f"Quantity: {qty_m}")
    if not price_ok:
        errors.append(f"Unit Price: {price_m}")

    if errors:
        # show the errors in the form as well as in a message box
        set_message(name_msg, name_m, name_ok)
        set_message(quantity_msg, qty_m, qty_ok)
        set_message(price_msg, price_m, price_ok)
        update_status()
        log_trace(summary, "Rejected", " ; ".join(errors))
        messagebox.showerror(
            "Invalid Input", "Please correct the following:\n\n" + "\n".join(errors)
        )
        return

    try:
        total = quantity * price # Total Value = Quantity x Unit Price
    except (TypeError, OverflowError): # extra safety net
        messagebox.showerror("Error", "Could not compute the total value.")
        return

    record_count += 1
    output_text.config(state="normal")
    if record_count == 1:
        output_text.delete("1.0", "end") # remove the placeholder text
    output_text.insert("end", f"Record #{record_count}\n", "head")
    output_text.insert("end", f"Product Name: {name}\n")
    output_text.insert("end", f"Quantity: {quantity}\n")
    output_text.insert("end", f"Unit Price: {PESO}{price:,.2f}\n")
    output_text.insert("end", f"Total Value: {PESO}{total:,.2f}\n")
    output_text.insert("end", "Status: Successfully Added\n", "ok")
    output_text.insert("end", "-" * 34 + "\n")
    output_text.see("end")
    output_text.config(state="disabled")

    log_trace(summary, "Product added", f"Successfully Added (Total {PESO}{total:,.2f})")
    messagebox.showinfo("Success", f"'{name}' was successfully added to the inventory.")
    clear_form(log=False)
    status_label.config(text="Product added successfully.", fg=GREEN)



# TASK 4 - CLEAR FORM
def clear_form(log=True):
    """Empty the 3 fields and reset the validation messages.
    Previously submitted records are NOT deleted."""
    name_var.set("")
    quantity_var.set("")
    price_var.set("")
    for lbl in (name_msg, quantity_msg, price_msg):
        lbl.config(text="")
    update_status()
    name_entry.focus_set()
    if log:
        log_trace("Click Clear Form", "Fields reset", "All fields emptied, messages reset")


def clear_inventory():
    """Separate function: removes all submitted records from the output."""
    global record_count
    if record_count == 0:
        messagebox.showinfo("Clear Inventory", "There are no records to clear.")
        return
    if messagebox.askyesno("Clear Inventory", "Delete ALL submitted inventory records?"):
        record_count = 0
        output_text.config(state="normal")
        output_text.delete("1.0", "end")
        output_text.insert("end", PLACEHOLDER)
        output_text.config(state="disabled")
        log_trace("Click Clear Inventory", "Records removed", "Inventory output cleared")



# TASK 1 - GUI LAYOUT

# HEADER
header = tk.Frame(root, bg=HEADER_BG, padx=14, pady=10)
header.pack(fill="x", padx=10, pady=(10, 6))
tk.Label(header, text="Robust Inventory Form", font=F_TITLE, bg=HEADER_BG, fg="white").pack(anchor="w")
tk.Label(header, text="Computer Shop Inventory Management", font=F_SUB, bg=HEADER_BG, fg="white").pack(anchor="w")

# BODY
body = tk.Frame(root, bg=BG)
body.pack(fill="both", expand=True, padx=10, pady=4)
body.columnconfigure(0, weight=1, uniform="col")
body.columnconfigure(1, weight=1, uniform="col")
body.rowconfigure(0, weight=1)

left = tk.Frame(body, bg=BG)
left.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
right = tk.Frame(body, bg=BG)
right.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
right.rowconfigure(0, weight=3)
right.rowconfigure(1, weight=2)
right.columnconfigure(0, weight=1)

# PRODUCT
info_panel = make_panel(left)
info_panel.pack(fill="x")
tk.Label(info_panel, text="Product Information", font=F_HEAD, bg=PANEL_BG, fg=FG).pack(anchor="w", pady=(0, 4))


def make_field(parent, caption, var, placeholder_hint):
    tk.Label(parent, text=caption, font=F_LABEL, bg=PANEL_BG, fg=FG).pack(anchor="w")
    entry = tk.Entry(
        parent, textvariable=var, font=F_ENTRY, bg=ENTRY_BG, fg=FG,
        insertbackground=FG, relief="flat", highlightthickness=1,
        highlightbackground=PANEL_BORDER, highlightcolor=BLUE,
    )
    entry.pack(fill="x", ipady=6, pady=(2, 0))
    msg = tk.Label(parent, text="", font=F_MSG, bg=PANEL_BG, fg=GREEN, anchor="w", justify="left")
    msg.pack(fill="x", pady=(2, 4))
    return entry, msg


name_entry, name_msg = make_field(info_panel, "Product Name", name_var, "Enter product name...")
quantity_entry, quantity_msg = make_field(info_panel, "Quantity", quantity_var, "Enter quantity...")
price_entry, price_msg = make_field(info_panel, f"Unit Price ({PESO})", price_var, "Enter unit price...")

btn_row = tk.Frame(info_panel, bg=PANEL_BG)
btn_row.pack(fill="x", pady=(4, 2))
btn_row.columnconfigure(0, weight=1, uniform="b")
btn_row.columnconfigure(1, weight=1, uniform="b")
submit_btn = tk.Button(
    btn_row, text="Submit Product", font=F_LABEL, bg=BLUE, fg="white",
    activebackground="#1d4ed8", activeforeground="white", relief="flat",
    cursor="hand2", command=submit_product,
)
submit_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4), ipady=6)
clear_btn = tk.Button(
    btn_row, text="Clear Form", font=F_LABEL, bg=ENTRY_BG, fg=FG,
    activebackground="#222", activeforeground=FG, relief="flat",
    highlightthickness=1, highlightbackground=PANEL_BORDER,
    cursor="hand2", command=clear_form,
)
clear_btn.grid(row=0, column=1, sticky="ew", padx=(4, 0), ipady=6)

# VALIDATION MESSAGES

status_panel = make_panel(left)
status_panel.pack(fill="x", pady=(8, 0))
tk.Label(status_panel, text="Validation Messages", font=F_HEAD, bg=PANEL_BG, fg=FG).pack(anchor="w")
status_label = tk.Label(
    status_panel, text="Show current form status here.", font=F_MSG,
    bg=PANEL_BG, fg=FG_MUTED, anchor="w", justify="left", wraplength=380,
)
status_label.pack(fill="x", pady=(2, 0))

# INVENTORY OUTPUT PANEL

out_panel = make_panel(right)
out_panel.grid(row=0, column=0, sticky="nsew")
tk.Label(out_panel, text="Inventory Output", font=F_HEAD, bg=PANEL_BG, fg=FG).pack(anchor="w", pady=(0, 4))
out_wrap = tk.Frame(out_panel, bg=PANEL_BG)
out_wrap.pack(fill="both", expand=True)
out_scroll = tk.Scrollbar(out_wrap)
out_scroll.pack(side="right", fill="y")
output_text = tk.Text(
    out_wrap, font=F_TEXT, bg=PANEL_BG, fg=FG, relief="flat", wrap="word",
    height=10, yscrollcommand=out_scroll.set, state="disabled",
)
output_text.pack(side="left", fill="both", expand=True)
out_scroll.config(command=output_text.yview)
output_text.tag_config("ok", foreground=GREEN)
output_text.tag_config("head", foreground="#7fb2ff", font=(F_TEXT[0], 10, "bold"))

PLACEHOLDER = "No products yet.\nSubmitted products appear here."
output_text.config(state="normal")
output_text.insert("end", PLACEHOLDER)
output_text.config(state="disabled")

tk.Button(
    out_panel, text="Clear Inventory", font=F_MSG, bg=ENTRY_BG, fg=FG,
    activebackground="#222", activeforeground=FG, relief="flat",
    highlightthickness=1, highlightbackground=PANEL_BORDER,
    cursor="hand2", command=clear_inventory,
).pack(anchor="e", pady=(6, 0))

# VALIDATION TRACE LOG PANEL

trace_panel = make_panel(right)
trace_panel.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
tk.Label(trace_panel, text="Validation Trace Log", font=F_HEAD, bg=PANEL_BG, fg=FG).pack(anchor="w")
tk.Label(
    trace_panel, text="Test input | Expected response | Actual response",
    font=F_MSG, bg=PANEL_BG, fg=FG,
).pack(anchor="w", pady=(0, 4))
trace_wrap = tk.Frame(trace_panel, bg=PANEL_BG)
trace_wrap.pack(fill="both", expand=True)
trace_scroll = tk.Scrollbar(trace_wrap)
trace_scroll.pack(side="right", fill="y")
trace_text = tk.Text(
    trace_wrap, font=(F_TEXT[0], 8), bg=PANEL_BG, fg=FG_MUTED, relief="flat",
    wrap="word", height=7, yscrollcommand=trace_scroll.set, state="disabled",
)
trace_text.pack(side="left", fill="both", expand=True)
trace_scroll.config(command=trace_text.yview)

# FOOTER
tk.Label(
    root, text="Robust Inventory Form | Group Tkinter Laboratory Activity 7",
    font=(FONT, 8), bg=BG, fg=FG_MUTED,
).pack(side="bottom", pady=(0, 6))


# TASK 2 - STRINGVARS TO VALIDATION CALLBACK
name_var.trace_add("write", validate_name)
quantity_var.trace_add("write", validate_quantity)
price_var.trace_add("write", validate_price)

# log what was typed when the user leaves each field
name_entry.bind("<FocusOut>", log_field_name)
quantity_entry.bind("<FocusOut>", log_field_quantity)
price_entry.bind("<FocusOut>", log_field_price)

# Enter key = Submit Product
root.bind("<Return>", lambda e: submit_product())

# initial state: no messages shown yet
update_status()
status_label.config(text="Show current form status here. Start typing...", fg=FG_MUTED)
name_entry.focus_set()

root.mainloop()