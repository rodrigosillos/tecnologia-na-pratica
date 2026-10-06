from datetime import date

data_texto = "2026-09-10"
data_despesa = date.fromisoformat(data_texto)
inicio = date(2026, 9, 1)
fim = date(2026, 10, 1)

print(data_despesa)
print("Ano:", data_despesa.year)
print("No período:", inicio <= data_despesa < fim)
