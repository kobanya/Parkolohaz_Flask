import csv
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Napló fájl elérési útvonala
naplo_file = 'naplo.csv'

# Parkolóhelyek JSON fájl elérési útvonala
parkolohelyek_file = 'parkolohelyek.json'

# Betöltjük a parkolóhelyeket a JSON fájlból
with open(parkolohelyek_file, 'r') as file:
    parkolohelyek = json.load(file)

# Lista az aktuálisan foglalt parkolóhelyekről
aktuális_parkolohelyek = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ellenorzes', methods=['POST'])
def api_ellenorzes():
    try:
        data = request.get_json()
        rendszam = data.get('rendszam', '')

        # Módosítás: Ellenőrizzük, hogy a rendszám már foglalt-e
        if rendszam in aktuális_parkolohelyek:
            parkolohely_szam = aktuális_parkolohelyek.index(rendszam) + 1
            fizetendo_dij = szamol_dij(rendszam)  # Számold ki a fizetendő díjat
            naplozas(rendszam, parkolohely_szam, "Kihajtás", fizetendo_dij)
            # Módosítás: Töröljük a rendszámot a foglalt helyek közül
            aktuális_parkolohelyek.remove(rendszam)
            return jsonify({"status": "Kihajtás", "dij": fizetendo_dij})
        else:
            # Módosítás: Az üres parkolóhely helyett rendszámot kell visszaadni
            parkolohely_szam = foglal_parkolohely(rendszam)
            naplozas(rendszam, parkolohely_szam, "Behajtás", 0)  # Kezdeti díj 0
            return jsonify({"parkolohely_szam": parkolohely_szam, "status": "Behajtás"})
    except Exception as e:
        return jsonify({"error": str(e)})

# Módosítás: Hozzunk létre egy új funkciót a parkolóhely foglalásához
def foglal_parkolohely(rendszam):
    for hely in parkolohelyek['parkolohelyek']:
        if not hely['foglalt']:
            hely['foglalt'] = True
            hely['rendszam'] = rendszam
            aktuális_parkolohelyek.append(rendszam)
            return hely['szam']
    return None

def szamol_dij(azonosito):
    # Jelenlegi időpont
    most = datetime.now()

    # Az előző belépés időpontja a naplóból
    elozo_belepes_idopont = None

    # Keressük meg az előző belépést az adott azonosítóval
    with open(naplo_file, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == azonosito and row[3] == "Behajtás":
                elozo_belepes_idopont = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
                break

    # Ha van előző belépés, akkor számoljuk ki a parkolás időtartamát másodpercekben
    if elozo_belepes_idopont:
        parkolas_idotartama = (most - elozo_belepes_idopont).total_seconds()
        fizetendo_dij = parkolas_idotartama * (10/60)  # 10 Ft percben
    else:
        fizetendo_dij = 0  # Ha nincs előző belépés, nincs díj

    return int(fizetendo_dij)  # Visszatérünk az egész számú díjjal

def naplozas(rendszam, parkolohely, status, dij):
    idopont = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(naplo_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([rendszam, parkolohely, idopont, status, dij])

if __name__ == '__main__':
    app.run(debug=True)
