from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from src.Modules.WebData.Infrastructure.Repositories.webDataRepository import WebDataRepository
import time



class WebDataService():
    def __init__(self):
        pass

    def conectionFirefox(self):
        options = Options()
        
        #serve para rodar em background, sem abrir o navegador
        options.add_argument("--headless")

        #isso faz o selenium não esperar o css do site carregar totalmente
        options.page_load_strategy = 'eager'

        #isso serve pra fingir que é um usuario de verdade
        options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0")

        self.driver = webdriver.Firefox(options=options)
        self.driver.set_window_size(1920, 1080)

    def searchApartament(self):

        self.driver.get("https://www.quintoandar.com.br/alugar/imovel/sao-paulo-sp-brasil/apartamento")

        ### tentando pegar 300 itens de uma vez

        self.elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="house-card-container-rent"]')

        while len(self.elements) < 300:

            seeMore = self.driver.find_element(By.ID, 'see-more')
            seeMore.click()

            time.sleep(2)
            self.elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="house-card-container-rent"]')

            print(f"\rApartamentos encontrados: {len(self.elements)}", end='', flush=True)

        print("\n")

    def searchURLs(self):
        ###Pegando URLs
        self.links = []
        for  index, element in enumerate(self.elements, start=1):
            link = element.find_element(By.TAG_NAME, 'a')
            url = link.get_attribute('href')
            self.links.append(url)

            percent_conclusion = (index/len(self.elements))*100

            print(f"\rResgatando URLs: {round(percent_conclusion, 2)}%      ", end='', flush=True)

        print('\n')

    def extractData(self):
        ###Extraindo Dados
        Data = []
        for i, urls in enumerate(self.links, start=1):
            property = {'id': i}
            #navega na mesma aba
            try:
                self.driver.get(urls)
                # print(index)

                time.sleep(1.5)

                # - preço do imovel
                price = self.driver.find_element(By.CSS_SELECTOR, 'div[class="_91tt-n"]')

                value_text = price.find_element(By.TAG_NAME, 'p')

                value_string = value_text.text

                clean_value = value_string.replace('Aluguel R$', '').strip()

                clean_value = clean_value.replace('.', '').replace(',', '.')

                value = float(clean_value)

                property['Price'] = value

                # - Bairro
                try:
                    raw_neighborhood = self.driver.find_element(By.CSS_SELECTOR, 'small[class="CozyTypography xih2fc pwAPLE"]')

                    raw_neighborhood_string = raw_neighborhood.text

                    clean_neighborhood = raw_neighborhood_string.replace(', São Paulo', '')

                    property['neighborhood'] = clean_neighborhood

                except:
                    property['neighborhood'] = 'Na'


                # - Informaçoes da tabela de cada apartamento
                informations = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="house-main-info"]')

                for inf in informations:
                    div_MuiBox = inf.find_elements(By.CSS_SELECTOR, 'div[class="MuiBox-root mui-2exznw"]')

                    for pa, divs in enumerate(div_MuiBox, start=1):
                        p_elements = divs.find_elements(By.TAG_NAME, 'p')

                        for p in p_elements:
                            # print(f"{p.text} -> {pa}")
                            match pa:
                                case 1:
                                    raw_m2 = p.text

                                    clean_m2 = raw_m2.replace('m²', '').strip()

                                    m2 = float(clean_m2)

                                    property['m2'] = m2

                                case 2:
                                    raw_room = p.text

                                    try:
                                    
                                        clean_room = (
                                            raw_room.replace('quarto', '')
                                            .replace('quartos', '')
                                            .replace('suítes', '')
                                            .replace('suíte', '')
                                            .replace('(', '')
                                            .replace(')', '')
                                            .strip()
                                        )

                                        room = int(clean_room)

                                        property['quartos'] = room 
                                    except:
                                        property['quartos'] = raw_room

                                case 3:
                                    raw_bathroom = p.text

                                    try:
                                                                    
                                        clean_bathroom = (
                                            raw_bathroom.replace('banheiros', '')
                                            .replace('banheiro', '')
                                            .replace('suítes', '')
                                            .replace('suíte', '')
                                            .replace('(', '')
                                            .replace(')', '')
                                            .strip()
                                        )

                                        bathroom = int(clean_bathroom)
                                        property['banheiros'] = bathroom

                                    except: 
                                        property['banheiros'] = raw_bathroom

                                case 4:
                                    raw_car_space = p.text

                                    if raw_car_space != '-':
                                        try:
                                            clean_space = raw_car_space.replace('vagas', '').replace('vaga', '').strip()
                                            
                                            space = int(clean_space)
        
                                            property['vagas'] = space
                                        except:
                                            property['vagas'] = 0

                                    else:
                                        property['vagas'] = 0

                Data.append(property)

                percent_extration = (i/len(self.elements))*100

                print(f"\rExtraindo dados: {round(percent_extration,2)}%", end='', flush=True)
            except:
                continue

        print("\n")

        #confecciona o csv
        repository = WebDataRepository()

        repository.createTable(Data)

        print("Extração Concluída!")

    def tearDown(self):
        self.driver.close()
    