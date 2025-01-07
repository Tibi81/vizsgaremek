## A projekt futtatása  

**Klónoza a projektet a GitHubról:**  
``` bash
git clone https://github.com/Tibi81/vizsgaremek.git
```
**Lépjen be a projekt mappájába:**  
```bash
cd vizsgaremek
```
**Hozza létre a virtuális környezetet:**  
```bash
python -m venv venv
```
**Aktiválja a virtuális környezetet:**  
```bash
venv\Scripts\activate
```
**Lépjen be az ecommerce mappába:**  
```bash
cd ecommerce
```
**Telepítse a szükséges csomagokat a requirements.txt fájl alapján:**  
```bash
pip install -r requirements.txt
```
**Lépjen be a config mappába:**  
```bash
cd config
```
**Hozzon létre egy .env nevű fájlt**   
**Irja bele az alábbi tartalmat majd mentsd el:**  
```bash
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_password
```
***Figyelem! Cserélje le a `"your_email@example.com"` és `"your_password"` helyét a saját email címére és jelszavára.***  
**Most már futtathatja a projektet ezzel a paranccsal**
```bash
python manage.py runserver


```
# E-commerce Project

Ez egy Django alapú e-kereskedelmi weboldal, amelyet vizsgamunka bemutatásaként fejlesztettünk.

## Élő Demó

⚠️ **Figyelem**: Ez az élő demó csak tesztelési célokat szolgál. Nem valós e-kereskedelmi oldal, és nem történik valódi tranzakció.

Kipróbálhatod az oldal élő <a href="https://sakafa.pythonanywhere.com" target="_blank">[DEMO]</a> verzióját

## Funkciók

- Felhasználói regisztráció
- Termékek listázása és részletező oldalak
- Bevásárlókosár funkció
- Rendelés feldolgozás
- Felhasználói vélemények és értékelések

