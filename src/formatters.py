#formato moneda Colombiana
def formato_moneda_co(valor):
    return f"$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# formateo de valores numericos
def formato_miles_co(valor):
    return f"{valor:,.0f}".replace(",", ".")
