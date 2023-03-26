import requests
from bs4 import BeautifulSoup
import re
import time
import atexit
import os
from dotenv import load_dotenv

#per ottenere il percorso assoluto del file "data" che si trova nella stessa directory dello script Python corrente
file = os.path.join(os.path.dirname(__file__), 'data')

#definisco un dizionario headers contenente l'header User-Agent che verrà utilizzato in seguito per le richieste HTTP.
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

#regex per estrapolare il prezzo
regex_price = r"(\d[\d\.]*)"

#Variabili ambiente
load_dotenv()
telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
telegram_user_id = os.getenv('TELEGRAM_USER_ID')

#dizionari utilizzati
container_html={}   # <sitoweb-prodotto> -> <componente html>
paths={}            # <sitoweb-prodotto> -> <url>
price_web={}        # <sitoweb-prodotto> -> <prezzo>
notify_price={}     # <sitoweb-prodotto> -> <stato> 

#funzione per leggere dal file
def read_file(path):
    rows = []
    try:
        with open(path, 'r') as file:
            for line in file:
                rows.append(line.strip()) 
    except FileNotFoundError:
        print(f"Error: file '{path}' not found!")
    return rows



def send_custom_message_on_telegram(message):
    # Costruzione dell'url per l'invio del messaggio
    send_message_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage?chat_id={telegram_user_id}&text={message}"

    # Invio del messaggio
    response = requests.get(send_message_url)

    if response.status_code == 200:
        print(f"Messaggio inviato con successo!")
    else:
        print(f"Si è verificato un errore nell'invio del messaggio. (Error: {response.status_code})")




#funzione che viene utilizzata se non si riesce a trovare il prezzo nel componente html specificato
def json_price(html):
    regex=r".*\"price\"\:\"([\d\.\,]+)\".*"
    match=re.search(regex, html)
    if match:
        price = float(match.group(1).replace(',', '.'))
        return price
    return None

#per ricavare il prezzo
def get_price(website,url):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()                         # Verifica se ci sono errori nella risposta HTTP
        soup = BeautifulSoup(response.text, 'html.parser')

        # Trova il prezzo utilizzando il selettore CSS corretto
        price_tag = soup.select_one(container_html[website])

        if price_tag is None:

            price_j=json_price(soup.prettify())
            if price_j == None: 
                print(f"Error: non è stato possibile trovare il prezzo su '{website}'")
                return -1
            return price_j


        price_str = price_tag.text.strip().replace(',', '.')
                
        match = re.search(regex_price, price_str)
        if match:

            price = float(match.group(1))
            return price
        
        else:

            price_j=json_price(soup.prettify())

            if price_j == None: 
                print("Error: controlla bene il contenitore dove è presente il prezzo!")
                return -1
            
            return price_j
        
    except requests.exceptions.RequestException as e:
        print(f'Errore nella richiesta HTTP')
        return -1
    except Exception as e:
        print(f'Error: {e}')
        return -1


#Funzione che utilizzo per vedere se un prezzo è aumentato o diminuito (insieme al dizionario notify_price)
# notify_price[sitoweb]=<numero>           numero: -1-> aumentato, 0->invariato, 1->diminuito, 2-> errore 
def check_price(name):
    current_price=get_price(name,paths[name])
    
    if current_price==None:
        return
    
    if current_price==-1:
        if price_web[name]!=0:
            notify_price[name]=2
            price_web[name]=0
        return 

    if price_web[name]==-1:
        price_web[name]=current_price
        notify_price[name]=0
        return
    

    if price_web[name]!=current_price:

        if price_web[name]<current_price:
            notify_price[name]=-1
        elif price_web[name]>current_price:
            notify_price[name]=1
        else:
            notify_price[name]=2
            
        price_web[name]=current_price
        return


# Creazione messaggio per invio
def create_message():

    message="Ecco un recap dei prezzi dei vari siti:\n"

    for name, type in notify_price.items():
        website, product = name.split('-')
        if type==0:
            message+=f"⚪ "#invariato
        elif type==1:
            message+=f"🔵 "#diminuito
        elif type==-1:
            message+=f"🟡 "#aumentato
        else:
            message+=f"🔴 "#errore
        message+=f"{product.capitalize()} ({website.capitalize()}): {price_web[name]} euro\n"

    return message
        

            
# Controllo se è cambiato qualche prezzo, in quel caso invia il recap (anche quando viene avviato lo invia)
def check_notification(first):
    notify=False
    for name, type in notify_price.items():
        if type!=0 or first:
            if first:
                first=False
            if not notify:
                send_custom_message_on_telegram(create_message())
                notify=True
            notify_price[name]=0

            
    

# Loop per invio dei message
# Legenda eventualmente commentabile
def start_scan():

    send_custom_message_on_telegram("Legenda:\n⚪ : nessuna modifica al prezzo\n🔵 : prezzo diminuito\n🟡 : prezzo aumentato\n🔴 : errore\nPrezzo non sempre giusto!")
    send_custom_message_on_telegram("Avviata scansione...🗿")
    first=True
    while(True):

        #Controllo ogni sito web inserito
        for name, url in paths.items():
            check_price(name)

        check_notification(first)
        first=False

        #controllo ogni ora (modificabile in base alle esigenze)
        time.sleep(3600)


#Estarre componenti html
# es. span.<classeSpan> , span[itemprop="<prezzo>"] , #<id>
#Annidati
# span.class1 span.class2

#   Main: si crea tutti i dizionari e avvia il tutto
def main():

    rows=read_file(file)

    i = 0
    while i < len(rows):
        name = rows[i]
        container = rows[i+1]
        url = rows[i+2]
        container_html[name] = container
        paths[name] = url
        price_web[name]=-1
        i += 3

    start_scan()
    

    

#   viene eseguito quando viene chiuso lo script
def cleanup():
    print("Lo script sta per essere terminato.")
    send_custom_message_on_telegram("Fine scansione 🤨")


atexit.register(cleanup)

if __name__ == '__main__':
    main()

'''
formato dati(data.txt):

<sitoweb>-<prodotto>
<componente html contenente prezzo> 
<url sito web>

componente html puo essere anche null, nel caso lo cerca se è presente come testo "price":"<prezzo>"

esempio:

amazon-xiaomi pad 5
span.a-offscreen
https://www.amazon.it/Xiaomi-128GB-Wi-Fi-Cosmic-Grigio/dp/B09CV54PHX/ref=sr_1_2?crid=3SG8Y3FTJOQQK&keywords=xiaomi+pad+5&qid=1679604001&sprefix=xiaomi+oad%2Caps%2C162&sr=8-2


'''