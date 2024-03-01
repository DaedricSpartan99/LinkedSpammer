# Breaking linkedin

## Script per automatizzare lavoro sbatta, da eseguire **in ordine**:

    1) company_people_search.py : a partire da una pagina (ben scelta) estrae una serie di pagine affiliate e mette i link in un file, è più per trovare aziende piccole italiane
    2) company_find_people.py : prende i profili trovati da 1) e estrae le persone che hanno come ruolo "director", "CEO" o simili. Non è perfetto può sbagliare, ma funziona abbastanza bene per essere usato. Anche lui mette i profili in un file
    3) brutally_connect.py : prende i profili trovati da 2) e stabilisce la connessione. Fa un output di quelli connessi

## Premesse

    - Se clonate questo repo, fate una copia della cartella altrove e non ri-pushate i dati: non vorrete mica pubblicare le vostre credenziali.
    - Se al primo script viene dato in seed una persona (al posto di una company), allora questo cerca delle connessioni di altre persone (ad albero: conoscenti di conoscenti  e così via)
    - Se l'algoritmo 2) si è sbagliato (ovvero vedo che la persona trovata non è chiaramente un ceo), è meglio il messaggio per digital nomads
    - La cartella "./outputs" deve esistere, altrimenti modificare i parametri perchè i file vengano trovati correttamente
    - Testato col profilo in inglese, non ancora in italiano

## Installazione

Se avete già settato un python environment eseguite su un terminale:

```
pip install -r requirements.txt
```

## Uso

Cercare la sezione "# %% Profile info, credentials and parameters", modificare in seguito le macro:

    - USERNAME : username linkedin
    - PASSWORD : password linkedin
    - LANG : "en" per inglese, "it" per italiano
    - BROWSER = 'firefox' per usare Firefox, 'chrome' per usare Chrome

As esempio:

```
USERNAME = "sticazzi@ciao.com"
PASSWORD = "daje"
LANG = "en"
BROWSER = 'firefox'
```

