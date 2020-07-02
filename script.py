import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
from textwrap3 import wrap
import datetime

conversie_date = {'ian':'Jan',
                  'feb':'Feb',
                  'mar':'Mar',
                  'apr':'Apr',
                  'mai':'May',
                  'iun':'Jun',
                  'iul':'Jul',
                  'aug':'Aug',
                  'sep':'Sep',
                  'oct':'Oct',
                  'noi':'Nov',
                  'dec':'Dec'}

print(3*'\n')
print('Se incarca numele jocurilor...\n')
with open(r'C:\Users\cydox\Desktop\olx_search\de_cautat.txt', 'r') as fisier:
    de_cautat = [joc.rstrip('\n').replace(' ','-') for joc in fisier]


print('Se genereaza link-urile de cautare...\n')

url_jocuri = {}
for joc in de_cautat:
    if joc.split('-')[-1].find('^') == -1:
        url_jocuri.update({joc:f'https://www.olx.ro/iasi_39939/q-{joc}/?currency=RON'})
    else:
        url_jocuri.update({joc: f'https://www.olx.ro/iasi_39939/q-{"-".join(joc.split("-")[:-1])}/'})

rezultat = []
print('Se itereaza prin fiecare link...\n')
for joc,url in url_jocuri.items():
    print(f'Se cauta anunturi cu "{joc.replace("-"," ")}"...')
    pagina_cautare_joc = requests.get(url)

    cod_html_pagina = BeautifulSoup(pagina_cautare_joc.text, 'html.parser')

    if str(cod_html_pagina).find('Nu am gasit anunturi') == -1:
        toate_anunturile = cod_html_pagina.find('table', id="offers_table")
        tabele_anunturi = toate_anunturile.find_all('tr', class_="wrap")

        if len(tabele_anunturi) == 1:
            print(f' S-a gasit "{len(tabele_anunturi)}" anunt')
        else:
            print(f' S-au gasit "{len(tabele_anunturi)}" anunturi')

        count_anunt = 1
        for tabel in tabele_anunturi:
            data_limita = datetime.datetime.strptime('1 Jan 0001', '%d %b %Y').date()
            print(f'  Se preiau informatiile din anuntul {count_anunt}...')
            rand = tabel.find('td', class_='offer')
            detalii = rand.find('td', class_='title-cell')
            if detalii != None:
                link_joc = detalii.find('a', href=True, class_='linkWithHash')['href']
                if str(link_joc).find('autovit.ro') == -1:

                    titlu_joc = detalii.find('strong').text.strip()
                    pret = rand.find('p', class_='price')
                    if pret:
                        pret = pret.text.strip()
                    else:
                        pret = 'nespecificat'

                    if len(joc.split('-')) > 1 and joc.split('-')[-1].find('^') != -1:
                        data_limita = joc.split('-')[-1].replace('^',' ') + ' 2020'
                        data_limita_original = data_limita.replace('2020', '')
                        for key, val in conversie_date.items():
                            if data_limita.find(key) != -1:
                                data_limita = datetime.datetime.strptime(data_limita.replace(key,val), '%d %b %Y').date()
                                break

                    data_publicarii = rand.find('td', class_='bottom-cell').find_all('small')[-1].text.strip().replace('  ',' ') + ' 2020'
                    data_publicarii_original = data_publicarii.replace('2020','')
                    if data_publicarii.find('Azi') != -1:
                        data_publicarii = datetime.datetime.now().date()
                    elif data_publicarii.find('Ieri') != -1:
                        data_publicarii = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
                    else:
                        for key, val in conversie_date.items():
                            if data_publicarii.find(key) != -1:
                                data_publicarii = datetime.datetime.strptime(data_publicarii.replace(key, val), '%d %b %Y').date()
                                break

                    if data_limita == datetime.datetime.strptime('1 Jan 0001', '%d %b %Y').date() or data_publicarii >= data_limita:
                        pagina_anunt_joc = BeautifulSoup(requests.get(link_joc).text,'html.parser')
                        descriere_anunt = "\n".join(wrap(pagina_anunt_joc.find('div', id='textContent').text.strip(), width=60))
                        nume_op = pagina_anunt_joc.find('div', class_='offer-user__actions').find('a')
                        if nume_op == None:
                            nume_op = pagina_anunt_joc.find('div', class_='offer-user__actions').find('h4').text.strip()
                        else:
                            nume_op = nume_op.text.strip()

                        if joc.split('-')[-1].find('^') == -1:
                            rezultat.append([joc.replace('-', ' '), titlu_joc, pret, data_publicarii_original, link_joc, descriere_anunt, nume_op])
                        else:
                            rezultat.append([" ".join(joc.split("-")[:-1]), titlu_joc, pret, data_publicarii_original, link_joc, descriere_anunt, nume_op])

                        count_anunt = count_anunt + 1
                    else:
                        if joc.split('-')[-1].find('^') == -1:
                            rezultat.append([joc.replace('-', ' '), f'anunt gasit out of limit date (publicat pe {data_publicarii_original})', '---', '---', '---', '---', '---'])
                        else:
                            rezultat.append([" ".join(joc.split("-")[:-1]), f'anunt gasit out of limit date (publicat pe {data_publicarii_original})', '---', '---', '---', '---', '---'])
        print()

    else:
        if joc.split('-')[-1].find('^') == -1:
            rezultat.append([joc.replace('-',' '), '0 anunturi' ,'---','---','---','---','---'])
        else:
            rezultat.append([" ".join(joc.split("-")[:-1]), '0 anunturi' ,'---','---','---','---','---'])
        print(f' Nu s-au gasit anunturi\n')

    if cod_html_pagina.find('div', class_='pager rel clr'):
        rezultat.append([joc.replace('-', ' '), 'sunt mai multe pagini!', url, '', '', '', ''])

print('Cautare completa!')

fisier = open(r'C:\Users\cydox\Desktop\olx_search\olx.txt','w', encoding='utf-8')
fisier.write(tabulate(sorted(rezultat, key=lambda x: x[1] != '0 anunturi'), headers= ['Nume joc', 'Titlu anunt', 'Pret', 'Data publicarii', 'Link anunt', 'Descriere anunt', 'Nume OP'], tablefmt="fancy_grid", numalign='center', stralign='center'))
fisier.close()









# categorie_joc = detalii.find('small').text.strip()
# rezultat.append([joc.replace('-',' '), titlu_joc, pret, data_publicarii, link_joc, categorie_joc, descriere_anunt, nume_op])
# rezultat.append([joc.replace('-',' '), '0 anunturi' ,'---','---','---','---','---','---'])
# rezultat.append([joc.replace('-', ' '), 'sunt mai multe pagini!', url, '', '', '', '', ''])
# fisier.write(tabulate(rezultat, headers= ['Nume joc', 'Titlu anunt', 'Pret', 'Data publicarii', 'Link anunt', 'Categorie joc', 'Descriere anunt', 'Nume OP'], tablefmt="fancy_grid", numalign='center', stralign='center'))
