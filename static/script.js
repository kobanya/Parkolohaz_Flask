function delayReload() {
         // Késleltetés beállítása 5 másodpercig (5000 milliszekundum)
         setTimeout(function() {
         // Újratöltés végrehajtása
          window.location.reload();
         }, 3000);       // 3000 ms = 3 másodperc
         }

        // Függvény a naplóadatok betöltéséhez a JSON fájlból
        function betoltNaploAdatok() {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/naplo_adatok', true); // naplo_adatok végpontot használjuk GET metódussal
            xhr.onreadystatechange = function() {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    if (xhr.status === 200) {
                        // Sikeres válasz, a JSON fájl tartalma itt lesz kezelve
                        var naploAdatok = JSON.parse(xhr.responseText);
                        var table = document.getElementById('naplo_adatok');

                        naploAdatok.forEach(function(data) {
                            var row = table.insertRow(-1);
                            var rendszamCell = row.insertCell(0);
                            var bejovetelCell = row.insertCell(1);
                            var kilepesCell = row.insertCell(2);
                            var parkolohelyCell = row.insertCell(3);
                            var parkolodijCell = row.insertCell(4); // Új cella hozzáadva a parkolódíjhoz

                            rendszamCell.textContent = data.rendszam;
                            bejovetelCell.textContent = data.status === "Behajtás" ? data.idopont : "";
                            kilepesCell.textContent = data.status === "Kihajtás" ? data.idopont : "";
                            parkolohelyCell.textContent = data.parkolohely; // Parkolóhely hozzáadása
                            parkolodijCell.textContent = data.parkolodij; // Parkolódíj hozzáadása
                        });
                    } else {
                        console.error('Hiba történt a napló adatok betöltése közben.');
                    }
                }
            };
            xhr.send();
        }

        // Függvény a parkolóhelyek megjelenítéséhez
        function megjelenitParkolohelyeket() {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/parkolohelyek', true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    if (xhr.status === 200) {
                        var parkolohelyek = JSON.parse(xhr.responseText);
                        var parkolohelyekDiv = document.getElementById('parkolohelyek');
                        parkolohelyekDiv.innerHTML = ''; // Div ürítése

                        // Parkolóhelyek megjelenítése
                        parkolohelyek.parkolohelyek.forEach(function(hely) {
                            var kartyaDiv = document.createElement('div');
                            kartyaDiv.className = hely.foglalt ? 'kartya foglalt' : 'kartya szabad';

                            // Módosítás: Az ikon hozzáadása a szabad kártyákhoz
                            if (!hely.foglalt) {
                                var ikonDiv = document.createElement('div');
                                ikonDiv.className = 'ikon';
                                kartyaDiv.appendChild(ikonDiv);
                            } else {
                                // Módosítás: Az ikon hozzáadása a foglalt kártyákhoz
                                var tiltottIkonDiv = document.createElement('div');
                                tiltottIkonDiv.className = 'tiltott_behajtas';
                                kartyaDiv.appendChild(tiltottIkonDiv);
                            }

                            // Módosítás: Rendszám nagyobb betűméret
                            var helySzam = document.createElement('p');
                            helySzam.className = 'rendszam'; // Módosítás: Hozzáadva a rendszám osztályt
                            helySzam.textContent = hely.szam;

                            var allapot = document.createElement('p');
                            allapot.textContent = hely.foglalt ?  hely.rendszam : 'Állapot: Szabad';

                            kartyaDiv.appendChild(helySzam);
                            kartyaDiv.appendChild(allapot);
                            parkolohelyekDiv.appendChild(kartyaDiv);
                        });
                    } else {
                        console.error('Hiba történt a parkolóhelyek lekérése közben.');
                    }
                }
            };
            xhr.send();
        }

        // Az oldal betöltésekor betöltjük a napló adatokat és megjelenítjük a parkolóhelyeket
        window.addEventListener('load', function() {
            betoltNaploAdatok();
            megjelenitParkolohelyeket();
        });

        // Input küldése ellenőrzésre
        document.getElementById('belepes_gomb').addEventListener('click', function() {

        // AJAX hívás a Flask szerverhez a rendszám elküldésével
        var rendszam = document.getElementById('rendszam').value;
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/ellenorzes', true);
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.onreadystatechange = function() {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    if (xhr.status === 200) {
                        // Sikeres válasz
                        var response = JSON.parse(xhr.responseText);
                        if (response.status === "MEGTELET") {
                            // Módosítás: Ha megtelt a parkolóház, megjelenítjük az "MEGTELET" üzenetet
                            document.getElementById('belepes_kihajtas').textContent = "MEGTELET";
                            document.getElementById('fizetendo_dij').textContent = '';
                        } else if (response.status === "Behajtás") {
                            // Módosítás: Megjelenítjük a parkolóhely számot behajtáskor
                            document.getElementById('belepes_kihajtas').textContent = `Ide álljon be: ${response.parkolohely_szam}`;
                            // Módosítás: Megjelenítjük a fizetendő díjat behajtáskor
                            document.getElementById('fizetendo_dij').textContent = '';
                        } else {
                            // Módosítás: Megjelenítjük a fizetendő díjat kihajtáskor
                            document.getElementById('fizetendo_dij').textContent = `Fizetendő díj: ${response.dij} Ft`;
                        }
                    } else {
                        // Hiba történt
                        alert('Hiba történt: ' + xhr.status);
                    }
                }
            };
            xhr.send(JSON.stringify({ rendszam: rendszam }));
        });

        // Fülek kezelése
        var naploTab = document.getElementById('naplo_tab');
        var egyesitettNaploTab = document.getElementById('egyesitett_naplo_tab');
        var naploTable = document.getElementById('naplo_table');
        var egyesitettNaploTable = document.getElementById('egyesitett_naplo_table');

        naploTab.addEventListener('click', function() {
            naploTab.classList.add('active');
            egyesitettNaploTab.classList.remove('active');
            naploTable.classList.add('active');
            egyesitettNaploTable.classList.remove('active');
        });

        egyesitettNaploTab.addEventListener('click', function() {
            naploTab.classList.remove('active');
            egyesitettNaploTab.classList.add('active');
            naploTable.classList.remove('active');
            egyesitettNaploTable.classList.add('active');
        });

        var serverUrl = 'http://localhost:5000'; // A szerver URL-je, ahol a szervered fut
