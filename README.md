Klónozd a projektet a GitHubról:   
``` bash
git clone https://github.com/Tibi81/vizsgaremek.git
```
Lépj be a projekt mappájába:
```bash
cd vizsgaremek
```
Hozzd létre a virtuális környezetet:
```bash
python -m venv ven
```
És aktiváld:
```bash
venv\Scripts\activate
```
Lépj be az ecommerce mappába:
```bash
cd ecommerce
```
Telepítsd a szükséges csomagokat a requirements.txt fájl alapján:
```bash
pip install -r requirements.txt
```
Lépj be a config mappába:
```bash
cd config
```
Hozz létre egy .env nevű fájlt
Ird bele az alábbi tartalmat majd mentsd el:
```bash
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_password
```
Figyelem! Cseréld le a your_email@example.com és your_password helyét a saját email címedre és jelszavadra.
