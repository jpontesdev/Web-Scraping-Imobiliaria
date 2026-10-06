import csv

class WebDataRepository():

    def __init__(self):
        pass

    def createTable(self, Data: list) -> str:
        name_csv = 'imoveis6.csv'
        
        # Pega as chaves do primeiro dicionário para usar como cabeçalho (colunas)
        header = Data[0].keys()

        # Abre o arquivo em modo de escrita ('w')
        with open(name_csv, mode='w', newline='', encoding='utf-8') as archive_csv:
            # Cria o objeto de escrita do CSV
            writer = csv.DictWriter(archive_csv, fieldnames=header)
            
            # Escreve a linha do cabeçalho
            writer.writeheader()
            
            # Escreve todas as linhas com os dados dos dicionários
            writer.writerows(Data)

        return f"Sucessfuly!"