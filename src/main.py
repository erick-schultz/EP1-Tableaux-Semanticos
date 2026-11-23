from src.parser import parse_sequente
from src.tableaux import provar_sequente

sequente = parse_sequente(input("Digite o sequente: "))

print(provar_sequente(sequente))
