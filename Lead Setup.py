import tkinter as tk
from tkinter import ttk

def extract_data():
    text = input_text.get("1.0", tk.END)
    lines = text.splitlines()
    data = {
        "Name": "",
        "Email": "",
        "Phone": "",
        "City": "",
        "Prov/State": "",
        "Products Interest": [],
        "Message": ""
    }

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("Name:"):
            data["Name"] = line.replace("Name:", "").strip()
        elif line.startswith("Email:"):
            data["Email"] = line.replace("Email:", "").strip()
        elif line.startswith("Phone:"):
            data["Phone"] = line.replace("Phone:", "").strip()
        elif line.startswith("City:"):
            data["City"] = line.replace("City:", "").strip()
        elif line.startswith("Prov/State:"):
            data["Prov/State"] = line.replace("Prov/State:", "").strip()
        elif line.startswith("Products Interest:"):
            products_text = line.replace("Products Interest:", "").strip()
            i += 1
            # Keep reading until you hit the next known field or the end
            while i < len(lines) and not any(lines[i].startswith(prefix) for prefix in ["Message:", "Name:", "Email:", "Phone:", "City:", "Prov/State:", "Products Interest:"]):
                products_text += " " + lines[i].strip()
                i += 1
            i -= 1  # step back so the loop processes the current line again
            # Split tags by comma, preserve multi-word phrases
            data["Products Interest"] = [p.strip() for p in products_text.split(",") if p.strip()]
        elif line.startswith("Message:"):
            i += 1
            message_lines = lines[i:]
            data["Message"] = "\n".join(message_lines).strip()
            break
        i += 1

    # Display result
    result_output.delete("1.0", tk.END)
    for key, value in data.items():
        if isinstance(value, list):
            value = ", ".join(value)
        result_output.insert(tk.END, f"{key}: {value}\n")

# GUI setup
root = tk.Tk()
root.title("Odoo Lead Parser")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

ttk.Label(frame, text="Paste Odoo CRM Text:").grid(row=0, column=0, sticky=tk.W)

input_text = tk.Text(frame, width=80, height=12)
input_text.grid(row=1, column=0, padx=5, pady=5)

ttk.Button(frame, text="Extract Info", command=extract_data).grid(row=2, column=0, pady=5)

ttk.Label(frame, text="Extracted Output:").grid(row=3, column=0, sticky=tk.W)

result_output = tk.Text(frame, width=80, height=12, background="#f0f0f0")
result_output.grid(row=4, column=0, padx=5, pady=5)

root.mainloop()
