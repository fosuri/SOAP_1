import requests
import xml.etree.ElementTree as ET
import mysql.connector


url = "http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso"

payload ="""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <FullCountryInfoAllCountries xmlns="http://www.oorsprong.org/websamples.countryinfo">
    </FullCountryInfoAllCountries>
  </soap:Body>
</soap:Envelope>"""


headers = {
    'Content-Type': 'text/xml; charset=utf-8'
}

response = requests.request("POST", url, headers=headers, data=payload)


ns = {
    'm': 'http://www.oorsprong.org/websamples.countryinfo'
}


db_connection = mysql.connector.connect(
    host="localhost",
    user="cdb",
    password="cdb",
    database="cdb"
)


cursor = db_connection.cursor()

# Парсинг XML
root = ET.fromstring(response.text)

country_infos = root.findall('.//m:tCountryInfo', ns)


def create_tables():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS countries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            iso_code VARCHAR(2) UNIQUE,
            name VARCHAR(255),
            capital_city VARCHAR(255),
            phone_code VARCHAR(10),
            continent_code VARCHAR(2),
            currency_iso_code VARCHAR(3),
            country_flag VARCHAR(255)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS country_languages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            country_iso_code VARCHAR(2),
            language_iso_code VARCHAR(3),
            language_name VARCHAR(255),
            FOREIGN KEY (country_iso_code) REFERENCES countries(iso_code)
        )
    """)


create_tables()


for country_info in country_infos:
    iso_code = country_info.find('m:sISOCode', ns).text
    name = country_info.find('m:sName', ns).text
    capital_city = country_info.find('m:sCapitalCity', ns).text
    phone_code = country_info.find('m:sPhoneCode', ns).text
    continent_code = country_info.find('m:sContinentCode', ns).text
    currency_iso_code = country_info.find('m:sCurrencyISOCode', ns).text
    country_flag = country_info.find('m:sCountryFlag', ns).text
    
    # Вставка информации о стране в базу данных
    insert_country_query = "INSERT INTO countries (iso_code, name, capital_city, phone_code, continent_code, currency_iso_code, country_flag) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    country_data = (iso_code, name, capital_city, phone_code, continent_code, currency_iso_code, country_flag)
    cursor.execute(insert_country_query, country_data)

    languages = []
    language_tags = country_info.findall('.//m:tLanguage', ns)
    for language_tag in language_tags:
        language_iso_code = language_tag.find('m:sISOCode', ns).text
        language_name = language_tag.find('m:sName', ns).text
        languages.append({"ISO Code": language_iso_code, "Name": language_name})


    insert_language_query = "INSERT INTO country_languages (country_iso_code, language_iso_code, language_name) VALUES (%s, %s, %s)"
    for language in languages:
        language_data = (iso_code, language["ISO Code"], language["Name"])
        cursor.execute(insert_language_query, language_data)
    
    print("IsoCode:", iso_code)
    print("Name:", name)
    print("Capital City:", capital_city)
    print("Phone Code:", phone_code)
    print("Continent Code:", continent_code)
    print("Currency ISO Code:", currency_iso_code)
    print("Country Flag:", country_flag)
    print("Languages:")
    for language in languages:
        print("\tISO Code:", language["ISO Code"])
        print("\tName:", language["Name"])
    print("--------------------")  

db_connection.commit()

cursor.close()
db_connection.close()

  


  