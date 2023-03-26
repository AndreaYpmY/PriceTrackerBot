# PriceTrackerBot
Questo bot raccoglie i prezzi di alcuni prodotti su vari siti di e-commerce e invia un riepilogo via messaggio.

## Requisiti
Per utilizzare il bot, è necessario:
Avere un account Telegram.

Creare un bot Telegram tramite *BotFather* e ottenere il token del bot.

Avere *Python 3* installato sul proprio computer.

Installare le dipendenze del progetto tramite il comando **pip install -r requirements.txt**.

## Utilizzo
Clonare il repository in una cartella sul proprio computer.

Creare un file **.env** nella stessa cartella del codice sorgente e inserire il token del bot e id dell'utente come segue: 
 ```
  TELEGRAM_BOT_TOKEN = '<token bot>'
  TELEGRAM_USER_ID = '<user id>'
 ```
Inserire i siti web e i prodotti di interesse nel file data con il seguente protocollo:
  ```
  <nome sito web>-<prodotto>
  <componente html contenente il prezzo> 
  <url sito web>
  ```
Eseguire lo script PriceTrackerBot.py per avviare il bot.

## Funzionalità
Il bot raccoglie i prezzi dei prodotti di interesse dai vari siti di e-commerce e invia un riepilogo via messaggio Telegram.

Non si può interagire con il bot tramite telegram, ha solo la funzionalità di aggiornarti su eventuali prezzi cambiati su prodotti di tuo interesse

## Licenza
Questo progetto è distribuito sotto la licenza MIT. Per maggiori informazioni, consultare il file LICENSE.
