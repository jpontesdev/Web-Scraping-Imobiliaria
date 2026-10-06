import os
from src.Modules.WebData.Application.Services.webDataService import WebDataService
from src.Modules.WebData.Application.Services.LinearRegressionService import LinearRegressionService

def main():
    print("1 - Pegar Dados e Armazenar em uma tabela csv\n2 - Realizar um Regressão Linear da Tabela")
    choice = input("Digite o número:")

    match(choice):
        case '1':
            runSearch = WebDataService()
            runSearch.conectionFirefox()
            runSearch.searchApartament()
            runSearch.searchURLs()
            runSearch.extractData()
            runSearch.tearDown()

        case '2':
            csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data_propriety copy.csv')
            regression = LinearRegressionService(csv_path)
            regression.clean_data()
            regression.run_eda()
            regression.run_statistical_analysis()
            regression.transform_features()
            regression.calculate_vif()
            regression.split_data()
            regression.train_and_compare()
            regression.interpret_coefficients()
            regression.plot_results()


if __name__ == "__main__":
    main()