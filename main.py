import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, static_url_path='/static')

# Napló fájl elérési útvonala (módosítva JSON fájlra)
naplo_file = 'naplo.json'

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

        for hely in parkolohelyek['parkolohelyek']:
            if hely['rendszam'] == rendszam:
                parkolohely_szam = hely['szam']
                fizetendo_dij = szamol_dij(rendszam)
                naplozas(rendszam, parkolohely_szam, "Kihajtás", fizetendo_dij)
                hely['foglalt'] = False
                hely['rendszam'] = ''
                with open(parkolohelyek_file, 'w') as json_file:
                    json.dump(parkolohelyek, json_file, indent=4)
                return jsonify({"status": "Kihajtás", "dij": fizetendo_dij})

        for hely in parkolohelyek['parkolohelyek']:
            if not hely['foglalt']:
                hely['foglalt'] = True
                hely['rendszam'] = rendszam
                naplozas(rendszam, hely['szam'], "Behajtás", 0)
                with open(parkolohelyek_file, 'w') as json_file:
                    json.dump(parkolohelyek, json_file, indent=4)
                return jsonify({"parkolohely_szam": hely['szam'], "status": "Behajtás"})

        return jsonify({"status": "Teltház"})
    except Exception as e:
        return jsonify({"error": str(e)})

def foglal_parkolohely(rendszam):
    for hely in parkolohelyek['parkolohelyek']:
        if not hely['foglalt']:
            hely['foglalt'] = True
            hely['rendszam'] = rendszam
            aktuális_parkolohelyek.append(rendszam)
            return hely['szam']
    return None

def szamol_dij(azonosito):
    most = datetime.now()
    elozo_belepes_idopont = None

    with open(naplo_file, mode='r') as file:
        for line in file:
            data = json.loads(line)
            if data["rendszam"] == azonosito and data["status"] == "Behajtás":
                elozo_belepes_idopont = datetime.strptime(data["idopont"], "%Y-%m-%d %H:%M:%S")
                break

    if elozo_belepes_idopont:
        parkolas_idotartama = (most - elozo_belepes_idopont).total_seconds()
        fizetendo_dij = parkolas_idotartama * 1  # Minden másodperc után 1 Ft (módosítottuk)
    else:
        fizetendo_dij = 0  # Ha nincs előző belépés, nincs díj

    return int(fizetendo_dij)

def naplozas(rendszam, parkolohely, status, parkolodij):
    idopont = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(naplo_file, 'a') as json_file:
        data = {
            "rendszam": rendszam,
            "parkolohely": parkolohely,
            "idopont": idopont,
            "status": status,
            "parkolodij": parkolodij
        }
        json.dump(data, json_file)
        json_file.write('\n')

@app.route('/parkolohelyek', methods=['GET'])
def api_parkolohelyek():
    return jsonify(parkolohelyek)

@app.route('/naplo_adatok', methods=['GET'])
def api_naplo_adatok():
    try:
        with open(naplo_file, 'r') as file:
            naplo_adatok = [json.loads(line) for line in file]
        return jsonify(naplo_adatok)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
