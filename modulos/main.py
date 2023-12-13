import requests
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
import os
from functools import partial
from re import findall

def get_user_page(user, page):
    url = f"https://letterboxd.com/{user}/watchlist/page/{page}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    titulos = []
    ul_element = soup.find('ul', class_=lambda x: x and 'poster-list' in x.split())

    if ul_element:
        # Encuentra todos los elementos li dentro del elemento ul
        li_elements = ul_element.find_all('li')

        # Itera sobre los elementos li
        for li_element in li_elements:
            div_element = li_element.find('div')
            link = div_element.get("data-target-link")
            img_element = div_element.find('img')
            titulos.append([img_element.get("alt"), link])

        return titulos
    else:
        raise RuntimeError
    
def get_page(url, page):
    url += f"/page/{page}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    ul_element = soup.find('ul', class_=lambda x: x and 'poster-list' in x.split())
    titulos = []
    if ul_element:
        # Encuentra todos los elementos li dentro del elemento ul
        li_elements = ul_element.find_all('li')

        # Itera sobre los elementos li
        for li_element in li_elements:
            div_element = li_element.find('div')
            link = div_element.get("data-target-link")
            img_element = div_element.find('img')
            titulos.append([img_element.get("alt"), link])
        return titulos
    else:
        raise RuntimeError

def get_user_watchlist(user):
    url = f"https://letterboxd.com/{user}/watchlist/"
    # print("URL:", url)
    response = requests.get(url)


    # Verifica si la solicitud fue exitosa (código de estado 200)
    if response.status_code != 200:
        raise RuntimeError
    else:
        soup = BeautifulSoup(response.text, 'html.parser')

        pagination_div = soup.find('div', class_=lambda x: x and 'pagination' in x.split())
        num_paginas = int(pagination_div.find_all('li')[-1].get_text())

        num_hilos = min(8, os.cpu_count() * 2)
        num_hilos = os.cpu_count() * 2

        get_page_from_user = partial(get_user_page, user)
        resultados = {}
        with ThreadPoolExecutor(max_workers=num_hilos) as executor:
            futures = [executor.submit(get_page_from_user, i) for i in range(1, num_paginas + 1)]

            # Utilizamos as_completed para obtener los resultados a medida que se completan
            for future in as_completed(futures):
                try:
                    result = future.result()
                    resultados[future] = result
                except Exception as e:
                    # Manejar excepciones si es necesario
                    print(f"Error: {e}")

        retorno = list(resultados.values())
        retorno = [titulo for lista in retorno for titulo in lista]
        return retorno

    
def get_list_content(url):
    response = requests.get(url)

    # Verifica si la solicitud fue exitosa (código de estado 200)
    retorno = []
    if response.status_code != 200:
        raise RuntimeError
    else:
        soup = BeautifulSoup(response.text, 'html.parser')

        pagination_div = soup.find('div', class_=lambda x: x and 'pagination' in x.split())
        if pagination_div != None:
            num_paginas = int(pagination_div.find_all('li')[-1].get_text())
        else:
            num_paginas = 1

        num_hilos = min(8, os.cpu_count() * 2)
        num_hilos = os.cpu_count() * 2

        get_page_from_list = partial(get_page, url)
        # with ThreadPoolExecutor(max_workers=num_hilos) as executor:
        #     executor.map(get_page_from_list, range(1, num_paginas + 1))

        resultados = {}
        with ThreadPoolExecutor(max_workers=num_hilos) as executor:
            futures = [executor.submit(get_page_from_list, i) for i in range(1, num_paginas + 1)]

            # Utilizamos as_completed para obtener los resultados a medida que se completan
            for future in as_completed(futures):
                try:
                    result = future.result()
                    resultados[future] = result
                except Exception as e:
                    # Manejar excepciones si es necesario
                    print(f"Error: {e}")


        retorno = list(resultados.values())
        retorno = [titulo for lista in retorno for titulo in lista]
        return retorno
    
def existe_usuario(user):
    url = f"https://letterboxd.com/{user}"
    # print("URL:", url)
    response = requests.get(url)

    return response.status_code == 200

def existe_lista(url):
    if is_list_url(url):
        return requests.get(url).status_code == 200
    else:
        return False


def is_list_url(value):
    return findall(pattern=r"https:\/\/letterboxd.com\/\w+\/list\/",
                    string=value) != []

def get_film_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    header = soup.find('section', class_=lambda x: x and 'film-header-lockup' in x.split())
    p_tag = header.find('p')
    
    año = p_tag.find('a').text


    director = p_tag.find('span', class_='prettify').text
    
    review = soup.find('div', class_=lambda x: x and 'review' in x.split())
    
    review = review.find('p').text
    
    return {
        'anio' : año,
        'director' : director,
        'review' : review
    }


            
if __name__ == "__main__":
    # users = ["eliseobndtti", "Justo14", "atylb"]
    # # users = ["Justo14"]
    # for user in users:
    #     t_inicio = time.time()
    #     retorno = get_user_watchlist(user)
    #     t_fin = time.time()
    #     print(user, len(retorno), f"Tardó {t_fin-t_inicio} segundos")
    #     # print(retorno)

    # # retorno = get_list_content("https://letterboxd.com/eliseobndtti/list/ciclo-de-verano-cinefilo-con-mi-amigo-atilio/")
    # # print(retorno)

    print(existe_usuario("Justo14"))


    

