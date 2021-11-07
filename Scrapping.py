from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
import json
import urllib3
urllib3.disable_warnings()
client = MongoClient('mongodb+srv://TestUser:Test1234@cluster0.dqz9b.mongodb.net/VehiclesData?retryWrites=true&w=majority')

db = client["<database>"]
collection = db["<collection>"]
Data = []
for a in range(2):
    current_page = 1
    total_pages = 100
    Data = []
    fileIndex = a + 1
    while current_page <= total_pages:

        url = 'https://usedabarth.co.uk/wp-content/themes/gsd-framework/ajax/ajax.php?price=&vehicle_age=&mileage=&make=ABARTH&open-filters=&sort=&key=vehicle-search&page='+str(current_page)+'&size=12&has_images=Y&retailer_id='
        webData=requests.get(url , verify = False)
        apiData = webData.json()
        total_pages = apiData['total-pages']
        current_page = apiData['current-page']
        print('Fetching data from page ', current_page, ' of ', total_pages)
        data = apiData['results']
        doc = BeautifulSoup(data , "html.parser")
        parentDivs = doc.find_all('div', class_ = 'listing-advert')
        for parentDiv in parentDivs:
            image = parentDiv.find('img')['data-src'].strip().split(' ')[0]
            title = parentDiv.find('a', class_ ='h5 brand-colour').text.strip()
            price = parentDiv.find('p', class_='vr h2').text.strip()
            address = parentDiv.find('p', class_='mb-0 light-grey small').text.strip()
            vehicleDetails = parentDiv.find('div', class_='spec-list vr2')
            registrationDate = ''
            mileage = ''
            fuel = ''
            transmission = ''
            for detail in vehicleDetails.find_all('p'):
                type = detail.find('i')['class']
                detail = detail.text.strip()
                if 'fa-gas-pump' in type:
                    fuel = detail
                if 'fa-cog' in type:
                    transmission = detail
                if 'fa-tachometer-alt' in type:
                    mileage = detail
                if 'fa-clipboard-check' in type:
                    registrationDate = detail
            itemTuple = {
                'Title' : title,
                'Image' : image,
                'Price' : price,
                'Address' : address,
                'VehicleDetails' : {
                    'RegistrationDate': registrationDate,
                    'Mileage': mileage,
                    'Fuel' : fuel,
                    'Transmission' : transmission
                }
            }

            if not any(d['Title'] == title and d['Image'] == image and d['Address'] == address for d in Data):
                Data.append(itemTuple)
        current_page += 1
    print(Data)

    with open('data'+str(fileIndex)+'.json', 'w') as f:
        json.dump(Data, f, ensure_ascii=False)
collection.insert_many(Data)
print("success")
