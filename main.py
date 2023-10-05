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
    parkolohelyek_data = json.load(file)

# Lista az aktuálisan foglalt parkolóhelyekről
aktuális_parkolohelyek = []

# Frissítjük a parkolóhelyek állapotát a JSON fájlban
def frissit_parkolohelyek_json():
    with open(parkolohelyek_file, 'w') as file:
        json.dump(parkolohelyek_data, file, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ellenorzes', methods=['POST'])
def api_ellenorzes():
    try:
        data = request.get_json()
        rendszam = data.get('rendszam', '')

        # Módosítás: Ellenőrizzük, hogy a rendszám már foglalt-e
        for hely in parkolohelyek_data['parkolohelyek']:
            if hely['rendszam'] == rendszam:
                parkolohely_szam = hely['szam']
                fizetendo_dij = szamol_dij(rendszam)  # Számold ki a fizetendő díjat
                naplozas(rendszam, parkolohely_szam, "Kihajtás")
                # Módosítás: Frissítjük a parkolóhely állapotát
                hely['foglalt'] = False
                hely['rendszam'] = ""
                frissit_parkolohelyek_json()
                return jsonify({"status": "Kihajtás", "dij": fizetendo_dij})

        # Módosítás: Az üres parkolóhely helyett rendszámot kell visszaadni
        parkolohely_szam = foglal_parkolohely(rendszam)
        naplozas(rendszam, parkolohely_szam, "Behajtás")
        return jsonify({"parkolohely_szam": parkolohely_szam, "status": "Behajtás"})
    except Exception as e:
        return jsonify({"error": str(e)})

# Módosítás: Hozzunk létre egy új funkciót a parkolóhely foglalásához
def foglal_parkolohely(rendszam):
    for hely in parkolohelyek_data['parkolohelyek']:
        if not hely['foglalt']:
            hely['foglalt'] = True
            hely['rendszam'] = rendszam
            frissit_parkolohelyek_json()
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
        fizetendo_dij = parkolas_idotartama * 10  # Minden másodperc után 10 Ft
    else:
        fizetendo_dij = 0  # Ha nincs előző belépés, nincs díj

    return int(fizetendo_dij)  # Visszatérünk az egész számú díjjal

def naplozas(rendszam, parkolohely, status):
    idopont = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(naplo_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([rendszam, parkolohely, idopont, status])

if __name__ == '__main__':
    app.run(debug=True)
