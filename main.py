import requests
from bs4 import BeautifulSoup
import sqlite3

url = 'https://ek.ua/ek-list.php?katalog_=189&save_podbor_=1&minPrice_=&maxPrice_=&sc_id_=980&pr_%5B%5D=29260&pr_%5B%5D=24105&pr_%5B%5D=36912&pr_%5B%5D=36356&pr_%5B%5D=38912&pr_%5B%5D=36051&pr_%5B%5D=35663&pr_%5B%5D=37775&pr_%5B%5D=46952&pr_%5B%5D=43493&pr_%5B%5D=43003&pr_%5B%5D=42256&pr_%5B%5D=44708&pr_%5B%5D=42257&pr_%5B%5D=44709&pr_%5B%5D=42258&pr_%5B%5D=47132&pr_%5B%5D=28817&pr_%5B%5D=28819&pr_%5B%5D=46951&pr_%5B%5D=45754&pr_%5B%5D=43908&pr_%5B%5D=42764&pr_%5B%5D=42763&pr_%5B%5D=43050'

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
}

# usd
req = requests.get('https://minfin.com.ua/currency/usd/', headers)
soup = BeautifulSoup(req.text, 'lxml')
usd = float(soup.find_all(class_='mfm-posr')[4].text.split()[0])
usd = round(usd * 100) / 100
print('USD:', usd)

# ETH
req = requests.get('https://www.investing.com/crypto/ethereum/eth-usd', headers)
soup = BeautifulSoup(req.text, 'lxml')
eph = float(soup.find_all(class_='text-2xl')[2].text.replace(',', ''))
print('EPH:', eph)

# Create SQL database
conn = sqlite3.connect('data.db')
cur = conn.cursor()
cur.execute('''DROP TABLE Videocard''')
cur.execute('''
    CREATE TABLE IF NOT EXISTS Videocard (
        label TEXT,
        model TEXT,
        price INTEGER,
        hash REAL
    )
''')
conn.commit()

# links to videocards
links = [
    'https://ek.ua/MSI-RX-580-GAMING-X-8G.htm',
    'https://ek.ua/ASUS-RADEON-RX-6600-DUAL.htm',
    'https://ek.ua/POWERCOLOR-RADEON-RX-6700-XT-RED-DEVIL.htm',
    'https://ek.ua/SAPPHIRE-NITROPLUS-RX-6900-XT-11308-03-20G.htm',
    'https://ek.ua/POWERCOLOR-RADEON-RX-6800-RED-DRAGON-AXRX-6800-16GBD6-3DHR-OC.htm',
    'https://ek.ua/GIGABYTE-RADEON-RX-6800-XT-AORUS-MASTER-16G.htm',
    'https://ek.ua/MSI-GEFORCE-GTX-1660-SUPER-VENTUS-XS-OC.htm',
    'https://ek.ua/GIGABYTE-GEFORCE-RTX-2060-D6-6G.htm',
    'https://ek.ua/MSI-GEFORCE-GTX-1660-VENTUS-XS-6G.htm',
    'https://ek.ua/GIGABYTE-GEFORCE-GTX-1660-TI-OC-6G.htm',
    'https://ek.ua/GIGABYTE-GEFORCE-RTX-3060-TI-GAMING-OC-LHR-8G.htm',
    'https://ek.ua/MSI-GEFORCE-RTX-3070-TI-VENTUS-3X-8G-OC.htm',
    'https://ek.ua/PALIT-GEFORCE-GTX-1660-TI-DUAL.htm',
    'https://ek.ua/PALIT-GEFORCE-RTX-2060-SUPER-DUAL.htm',
    'https://ek.ua/MSI-GEFORCE-RTX-3090-VENTUS-3X-24G-OC.htm',
    'https://ek.ua/MSI-GEFORCE-RTX-3080-TI-VENTUS-3X-12G-OC.htm',
    'https://ek.ua/ZOTAC-GEFORCE-RTX-3080-TRINITY-OC-LHR.htm',
    'https://ek.ua/ZOTAC-GEFORCE-RTX-3070-TWIN-EDGE-OC-WHITE-EDITION-LHR.htm'
]

for link in links:
    req = requests.get(link, headers)
    soup = BeautifulSoup(req.text, 'lxml')

    # price
    price = soup.find(itemprop="lowPrice").text.split()
    price = round(float(''.join(price)) * 100) / 100

    # full label
    name = soup.find(itemprop="name").text.split()[1]

    # model
    model_full = soup.find_all(class_="op3")
    for item in model_full:
        if 'NVIDIA' in item.text or 'AMD' in item.text:
            model_full = item.text
            break
    
    model = list()
    if model_full.find('GeForce') != -1:
        for item in model_full.split():
            if item != 'GeForce':
                model.append(item)
        model = ' '.join(model)
    elif model_full.find('Radeon') != -1:
        for item in model_full.split():
            if item != 'Radeon':
                model.append(item)
        model = ' '.join(model)
        if model == 'AMD RX 580':
            model = model + ' 8GB'

    # hash
    req = requests.get('https://www.kryptex.org/ru/best-gpus-for-mining', headers)
    soup = BeautifulSoup(req.text, 'lxml')

    mh = float(soup.find(text=model).parent.parent.parent.parent.parent.find(class_='text-middle').parent.text.split()[0])

    cur.execute('''INSERT INTO Videocard (label, model, price, hash) VALUES ( ?, ?, ?, ? )''', (name, model, price, mh))
    conn.commit()

print('DONE')
