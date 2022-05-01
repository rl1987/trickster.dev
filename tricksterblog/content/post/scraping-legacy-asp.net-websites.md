+++
author = "rl1987"
title = "Scraping legacy ASP.NET websites"
date = "2022-05-02"
draft = true
tags = ["scraping", "python"]
+++

WRITEME: exploring the site and planning the code

```
curl 'https://publicaccess.claytoncountyga.gov/search/advancedsearch.aspx?mode=advanced' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' \
  -H 'Accept-Language: en-GB,en-US;q=0.9,en;q=0.8' \
  -H 'Cache-Control: max-age=0' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Cookie: ASP.NET_SessionId=5zbmmioup1jtvyidmrllbk3y; DISCLAIMER=1' \
  -H 'Origin: https://publicaccess.claytoncountyga.gov' \
  -H 'Referer: https://publicaccess.claytoncountyga.gov/search/advancedsearch.aspx?mode=advanced' \
  -H 'Sec-Fetch-Dest: document' \
  -H 'Sec-Fetch-Mode: navigate' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Sec-Fetch-User: ?1' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36' \
  -H 'sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  --data-raw '__EVENTTARGET=&__EVENTARGUMENT=&__VIEWSTATE=QL5SNhNFfFnBb7b4DtyY96KtZfoOELZgX2ocZ3TbFJ8fXXjiFrP3YoMdN4tbQaFgYrpi6YXyRLBB9cKrBja45rqOV01nCJfwqYr4yiFy%2FY%2FlSjsDmB0sSZZukGHaj%2BeSsUOrYYI%2B0nxrQ8KQGBtbq5z1x562R6okx9cJpEJBwbF3evV2qMPQrbSYljFVDWthUtuY79VM57peH1hltn%2Fjd9mPKHphbUlLfdJPTYalCjOG0b1%2B55I98Z9m1Yo%2FZmlRPyC0dNEpZ1NXuVmZ5CYysmWLs0rCUT0ISpZZ436liV5M8Na%2FdE09bwFkWXoFgqmWU2ldxR%2BGnDew5ZpJtlizmldcRyuqgNX33kWGEjjW%2FY9e%2FuqdX1ZgdizzSHagwblv0%2BmGikZ4uzo6pzatN21staAOBMUNxxuiqAQBCX%2Fzpn54LPqvhkqWDyyCk4cVd%2F87jGmHCdYaHA15048FeoHCG3Ra101%2B6CHalur7VldWA5pu288tbGCTWhxSLknohMlDWPsrvoLRrVdBZhh0eQavoEdsqJiLGili1%2B4aKEsdch6IpgE3%2FW2KnecseGhfvlT132Tq9mUHjWVEuLYbm7LwhQ%3D%3D&__VIEWSTATEGENERATOR=81E50120&__EVENTVALIDATION=OfiCDrhk%2F7nBQXu%2BF7%2FHpdUOvmDSTUs9qP2MZPIOh6agOkKfNTT1BAGpbZLQqe7QUUBuOkvT1uFiIdGa3n9JVkt10MXdyH09K3Xzy7sh7iE4nKhMde815zPrMoxtRwDniItUNoxNJwJ%2FFszKmejvkRpL5gAK8XpakkBbrfV2kwC7IA8TCDv1KHZAmZcvNptUiGCHCACjOZepl24QvvFP3IbhFWH8kaYQVgqETSHGHWmFgTuaU9X41uYABa6y0%2BplTPSBbAscfodjbOwQps81L80ZXFvCc0ZmqEgYa0ex7h5ytK74Z82HRvbhDy4HpQNa5CD794vkI8gFqAlv0so5Mb7gGSGN0y%2BdAhkWpq9euuZn8IVM34gjFk%2FWUp3SW%2FA3QHeM7H6U7dpO0sqvOcQZ%2FAao%2FF3v5R0otHgA7loURTzgTq2kuDqsc4jwdMI8NJH%2F3e9b25e1jPNc0%2BKLubSEA1rr4r8HOrU6wLjmn7XNpMfGLPyoy%2F%2FgN8PdAG4ZAXeeUPaT1F%2FS1TMox3XIqgd9xkUsn3R4ZeeGN%2FEaEXdLUTs%3D&PageNum=&SortBy=PARID&SortDir=+asc&PageSize=15&hdTaxYear=&hdAction=&hdCriteria=price%7C1000000%7E2000000&hdCriteriaLov=&hdCriteriaTypes=N%7CN%7CC%7CC%7CC%7CN%7CC%7CC%7CN%7CD%7CN%7CN%7CC%7CC%7CC%7CN%7CN&hdLastState=1&hdReset=&hdName=&hdSelectedQuery=0&mode=&hdSearchType=AdvSearch&hdListType=&hdIndex=&hdSelected=&hdCriteriaGroup=&hdCriterias=taxyr%7Cbathrooms%7Cbedrooms%7CClass%7Cluc%7Csfla%7Cnbhd%7Cowner%7Cprice%7Csalesdate%7Ccom_sf%7Cstories%7Cadrstr%7Cstyle%7Ctaxdist%7Cyr_com%7Cyr_buitl&hdSelectAllChecked=false&sCriteria=9&ctl01%24cal1=&ctl01%24cal1%24dateInput=&ctl01_cal1_dateInput_ClientState=%7B%22enabled%22%3Atrue%2C%22emptyMessage%22%3A%22%22%2C%22validationText%22%3A%22%22%2C%22valueAsString%22%3A%22%22%2C%22minDateStr%22%3A%221900-01-01-00-00-00%22%2C%22maxDateStr%22%3A%222099-12-31-00-00-00%22%2C%22lastSetTextBoxValue%22%3A%22%22%7D&ctl01_cal1_calendar_SD=%5B%5D&ctl01_cal1_calendar_AD=%5B%5B1900%2C1%2C1%5D%2C%5B2099%2C12%2C30%5D%2C%5B2022%2C5%2C1%5D%5D&ctl01_cal1_ClientState=%7B%22minDateStr%22%3A%221900-01-01-00-00-00%22%2C%22maxDateStr%22%3A%222099-12-31-00-00-00%22%7D&txtCrit=1000000&ctl01%24cal2=&ctl01%24cal2%24dateInput=&ctl01_cal2_dateInput_ClientState=%7B%22enabled%22%3Atrue%2C%22emptyMessage%22%3A%22%22%2C%22validationText%22%3A%22%22%2C%22valueAsString%22%3A%22%22%2C%22minDateStr%22%3A%221900-01-01-00-00-00%22%2C%22maxDateStr%22%3A%222099-12-31-00-00-00%22%2C%22lastSetTextBoxValue%22%3A%22%22%7D&ctl01_cal2_calendar_SD=%5B%5D&ctl01_cal2_calendar_AD=%5B%5B1900%2C1%2C1%5D%2C%5B2099%2C12%2C30%5D%2C%5B2022%2C5%2C1%5D%5D&ctl01_cal2_ClientState=%7B%22minDateStr%22%3A%221900-01-01-00-00-00%22%2C%22maxDateStr%22%3A%222099-12-31-00-00-00%22%7D&txtCrit2=2000000&txCriterias=9&selSortBy=PARID&selSortDir=+asc&searchOptions%24hdBeta=' \
  --compressed
```

```python3
import requests

cookies = {
    "ASP.NET_SessionId": "5zbmmioup1jtvyidmrllbk3y",
    "DISCLAIMER": "1",
}

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    # Requests sorts cookies= alphabetically
    # 'Cookie': 'ASP.NET_SessionId=5zbmmioup1jtvyidmrllbk3y; DISCLAIMER=1',
    "Origin": "https://publicaccess.claytoncountyga.gov",
    "Referer": "https://publicaccess.claytoncountyga.gov/search/advancedsearch.aspx?mode=advanced",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}

params = {
    "mode": "advanced",
}

data = {
    "__VIEWSTATE": [
        "QL5SNhNFfFnBb7b4DtyY96KtZfoOELZgX2ocZ3TbFJ8fXXjiFrP3YoMdN4tbQaFgYrpi6YXyRLBB9cKrBja45rqOV01nCJfwqYr4yiFy/Y/lSjsDmB0sSZZukGHaj+eSsUOrYYI+0nxrQ8KQGBtbq5z1x562R6okx9cJpEJBwbF3evV2qMPQrbSYljFVDWthUtuY79VM57peH1hltn/jd9mPKHphbUlLfdJPTYalCjOG0b1+55I98Z9m1Yo/ZmlRPyC0dNEpZ1NXuVmZ5CYysmWLs0rCUT0ISpZZ436liV5M8Na/dE09bwFkWXoFgqmWU2ldxR+GnDew5ZpJtlizmldcRyuqgNX33kWGEjjW/Y9e/uqdX1ZgdizzSHagwblv0+mGikZ4uzo6pzatN21staAOBMUNxxuiqAQBCX/zpn54LPqvhkqWDyyCk4cVd/87jGmHCdYaHA15048FeoHCG3Ra101+6CHalur7VldWA5pu288tbGCTWhxSLknohMlDWPsrvoLRrVdBZhh0eQavoEdsqJiLGili1+4aKEsdch6IpgE3/W2KnecseGhfvlT132Tq9mUHjWVEuLYbm7LwhQ=="
    ],
    "__VIEWSTATEGENERATOR": ["81E50120"],
    "__EVENTVALIDATION": [
        "OfiCDrhk/7nBQXu+F7/HpdUOvmDSTUs9qP2MZPIOh6agOkKfNTT1BAGpbZLQqe7QUUBuOkvT1uFiIdGa3n9JVkt10MXdyH09K3Xzy7sh7iE4nKhMde815zPrMoxtRwDniItUNoxNJwJ/FszKmejvkRpL5gAK8XpakkBbrfV2kwC7IA8TCDv1KHZAmZcvNptUiGCHCACjOZepl24QvvFP3IbhFWH8kaYQVgqETSHGHWmFgTuaU9X41uYABa6y0+plTPSBbAscfodjbOwQps81L80ZXFvCc0ZmqEgYa0ex7h5ytK74Z82HRvbhDy4HpQNa5CD794vkI8gFqAlv0so5Mb7gGSGN0y+dAhkWpq9euuZn8IVM34gjFk/WUp3SW/A3QHeM7H6U7dpO0sqvOcQZ/Aao/F3v5R0otHgA7loURTzgTq2kuDqsc4jwdMI8NJH/3e9b25e1jPNc0+KLubSEA1rr4r8HOrU6wLjmn7XNpMfGLPyoy//gN8PdAG4ZAXeeUPaT1F/S1TMox3XIqgd9xkUsn3R4ZeeGN/EaEXdLUTs="
    ],
    "SortBy": ["PARID"],
    "SortDir": [" asc"],
    "PageSize": ["15"],
    "hdCriteria": ["price|1000000~2000000"],
    "hdCriteriaTypes": ["N|N|C|C|C|N|C|C|N|D|N|N|C|C|C|N|N"],
    "hdLastState": ["1"],
    "hdSelectedQuery": ["0"],
    "hdSearchType": ["AdvSearch"],
    "hdCriterias": [
        "taxyr|bathrooms|bedrooms|Class|luc|sfla|nbhd|owner|price|salesdate|com_sf|stories|adrstr|style|taxdist|yr_com|yr_buitl"
    ],
    "hdSelectAllChecked": ["false"],
    "sCriteria": ["9"],
    "ctl01_cal1_dateInput_ClientState": [
        '{"enabled":true,"emptyMessage":"","validationText":"","valueAsString":"","minDateStr":"1900-01-01-00-00-00","maxDateStr":"2099-12-31-00-00-00","lastSetTextBoxValue":""}'
    ],
    "ctl01_cal1_calendar_SD": ["[]"],
    "ctl01_cal1_calendar_AD": ["[[1900,1,1],[2099,12,30],[2022,5,1]]"],
    "ctl01_cal1_ClientState": [
        '{"minDateStr":"1900-01-01-00-00-00","maxDateStr":"2099-12-31-00-00-00"}'
    ],
    "txtCrit": ["1000000"],
    "ctl01_cal2_dateInput_ClientState": [
        '{"enabled":true,"emptyMessage":"","validationText":"","valueAsString":"","minDateStr":"1900-01-01-00-00-00","maxDateStr":"2099-12-31-00-00-00","lastSetTextBoxValue":""}'
    ],
    "ctl01_cal2_calendar_SD": ["[]"],
    "ctl01_cal2_calendar_AD": ["[[1900,1,1],[2099,12,30],[2022,5,1]]"],
    "ctl01_cal2_ClientState": [
        '{"minDateStr":"1900-01-01-00-00-00","maxDateStr":"2099-12-31-00-00-00"}'
    ],
    "txtCrit2": ["2000000"],
    "txCriterias": ["9"],
    "selSortBy": ["PARID"],
    "selSortDir": [" asc"],
}

response = requests.post(
    "https://publicaccess.claytoncountyga.gov/search/advancedsearch.aspx",
    params=params,
    cookies=cookies,
    headers=headers,
    data=data,
)

print(response)

assert "LGS HOLDING GROUP 2013 LLC" in response.text
```

```python
import requests

cookies = {
    "DISCLAIMER": "1",
}

params = {
    "mode": "advanced",
}

data = {
    "__VIEWSTATE": [
        "QL5SNhNFfFnBb7b4DtyY96KtZfoOELZgX2ocZ3TbFJ8fXXjiFrP3YoMdN4tbQaFgYrpi6YXyRLBB9cKrBja45rqOV01nCJfwqYr4yiFy/Y/lSjsDmB0sSZZukGHaj+eSsUOrYYI+0nxrQ8KQGBtbq5z1x562R6okx9cJpEJBwbF3evV2qMPQrbSYljFVDWthUtuY79VM57peH1hltn/jd9mPKHphbUlLfdJPTYalCjOG0b1+55I98Z9m1Yo/ZmlRPyC0dNEpZ1NXuVmZ5CYysmWLs0rCUT0ISpZZ436liV5M8Na/dE09bwFkWXoFgqmWU2ldxR+GnDew5ZpJtlizmldcRyuqgNX33kWGEjjW/Y9e/uqdX1ZgdizzSHagwblv0+mGikZ4uzo6pzatN21staAOBMUNxxuiqAQBCX/zpn54LPqvhkqWDyyCk4cVd/87jGmHCdYaHA15048FeoHCG3Ra101+6CHalur7VldWA5pu288tbGCTWhxSLknohMlDWPsrvoLRrVdBZhh0eQavoEdsqJiLGili1+4aKEsdch6IpgE3/W2KnecseGhfvlT132Tq9mUHjWVEuLYbm7LwhQ=="
    ],
    "__VIEWSTATEGENERATOR": ["81E50120"],
    "__EVENTVALIDATION": [
        "OfiCDrhk/7nBQXu+F7/HpdUOvmDSTUs9qP2MZPIOh6agOkKfNTT1BAGpbZLQqe7QUUBuOkvT1uFiIdGa3n9JVkt10MXdyH09K3Xzy7sh7iE4nKhMde815zPrMoxtRwDniItUNoxNJwJ/FszKmejvkRpL5gAK8XpakkBbrfV2kwC7IA8TCDv1KHZAmZcvNptUiGCHCACjOZepl24QvvFP3IbhFWH8kaYQVgqETSHGHWmFgTuaU9X41uYABa6y0+plTPSBbAscfodjbOwQps81L80ZXFvCc0ZmqEgYa0ex7h5ytK74Z82HRvbhDy4HpQNa5CD794vkI8gFqAlv0so5Mb7gGSGN0y+dAhkWpq9euuZn8IVM34gjFk/WUp3SW/A3QHeM7H6U7dpO0sqvOcQZ/Aao/F3v5R0otHgA7loURTzgTq2kuDqsc4jwdMI8NJH/3e9b25e1jPNc0+KLubSEA1rr4r8HOrU6wLjmn7XNpMfGLPyoy//gN8PdAG4ZAXeeUPaT1F/S1TMox3XIqgd9xkUsn3R4ZeeGN/EaEXdLUTs="
    ],
    "SortBy": ["PARID"],
    "SortDir": [" asc"],
    "PageSize": ["15"],
    "hdCriteria": ["price|1000000~2000000"],
    "hdCriteriaTypes": ["N|N|C|C|C|N|C|C|N|D|N|N|C|C|C|N|N"],
    "hdLastState": ["1"],
    "hdSelectedQuery": ["0"],
    "hdSearchType": ["AdvSearch"],
    "hdCriterias": [
        "taxyr|bathrooms|bedrooms|Class|luc|sfla|nbhd|owner|price|salesdate|com_sf|stories|adrstr|style|taxdist|yr_com|yr_buitl"
    ],
    "hdSelectAllChecked": ["false"],
    "sCriteria": ["9"],
    "txtCrit": ["1000000"],
    "txtCrit2": ["2000000"],
    "txCriterias": ["9"],
    "selSortBy": ["PARID"],
    "selSortDir": [" asc"],
}

response = requests.post(
    "https://publicaccess.claytoncountyga.gov/search/advancedsearch.aspx",
    params=params,
    cookies=cookies,
    data=data,
)

print(response)

assert "LGS HOLDING GROUP 2013 LLC" in response.text
```

```
curl 'https://publicaccess.claytoncountyga.gov/search/advancedsearch.aspx?mode=advanced' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' \
  -H 'Accept-Language: en-GB,en-US;q=0.9,en;q=0.8' \
  -H 'Cache-Control: max-age=0' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Cookie: ASP.NET_SessionId=5zbmmioup1jtvyidmrllbk3y; DISCLAIMER=1' \
  -H 'Origin: https://publicaccess.claytoncountyga.gov' \
  -H 'Referer: https://publicaccess.claytoncountyga.gov/search/advancedsearch.aspx?mode=advanced' \
  -H 'Sec-Fetch-Dest: document' \
  -H 'Sec-Fetch-Mode: navigate' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Sec-Fetch-User: ?1' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36' \
  -H 'sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  --data-raw '__EVENTTARGET=&__EVENTARGUMENT=&__VIEWSTATE=xp%2BU7xWIH%2FWkG8AjGBqENMMc%2FlJWzEPo8hVNxOMXvVHVE6DLDW15N7QUlsVAmirgwz3l8N9B2Bao8Krnu1WzlljJr5ULUpOe3FrjCr0ByGJxuYXs8KRohuPMS00PQpVIYnQdeOLaUsr7cm8i2qOmGqgXtLrYRe4PfHO1RezWXMmvuM6LhiA3kZ2SHixuAsXKJC7Y1V7D6j5Ym5magtFXe8GQIG%2FHSC8uhY6ciEpbHrpCEeDJsXtyuOmk93pBrnvk%2BnJsWidtubDTPFQSWKwo0J0tH5gvf9ePUjCrJOGKfDzBJ%2BY03TPxmBFkDSwX%2BLct3N%2B0gmmYifB9YaZakj1fG90TyuxhXgnmh1xBHTFqQE5ANNBXuBAlyikA6NfDIlg1NWQINT%2BiLSurkNHLMYpvOPiUT183D5ZYr0l5kMnHFly0ESEbqLyVCcxWOybiaCYiq4zS7%2FgFWhQ9n59d13y59oJHpyVhGvijTaTSvGaqalY9ZLrV11hiXGh1XQySbJX%2Bt4ku%2FioO5IaIYI93Pv8k163sRczbLoNijz5qRFVmtjrrLXAkrZHMZP6s6QBG67W1MSFEQF9Evn5heWX9PR%2FsfWa6jMeh3jP5u72TZteV8g4%3D&__VIEWSTATEGENERATOR=81E50120&__EVENTVALIDATION=JGlJpwTn%2Bzu8GzcJc0cWEZ2W46%2FxFsJKpBB6bL0XdXJXlE35rX3XiuWLCIFtcxWKdEHUHnOOrPR0aNbsfhqF3DDQJFkV%2BLb95S%2Fgn8GigaiPWiB9kTgAR7Al8doUG5V8LLYbpzb9LbDEg3ogCxansImqtx9fEu7usd6IxJWukxLhUor43DuBIGoDXeFIkTCa2ZcPOvfRDulGfsDlI3losFm%2BSFFiaCan9JgvgBWCJGnctSEd%2B7K5dGNWootxCprge3JHMN2koEkUx%2BnHFh8WzcBiwC4uAoYzSgETGI8yImOqYoD4HlW3WC3XgqsWTMU5oC4ICrut5g6fbBl9Y78lMtk0z8tWVyl6KYAT61lzk39hnOjKqtIQDeXYIoBVdqDRarOiaaQD5wIZgc8aUy1wh6auyT3SvnMTLbhBmUF5xKhyczsCjHAON3zbyt2ITbY77QGWx3KCoFkDNW4hLZCmtWXUR5Jpr44UyFK0Gdqfd7v8CQfDi2FyG2pxbdwB3f21ckA0C0cNknAb%2BtONxXwwhzHz%2FNmka7cuzALQgX41oQyVfW2bM%2Fhe5G4Lil1M55bCEytG93p3Vw9sx%2BHeXJb0kVcSh39Q00rLSYUiCM%2Bd3N0op25g35PooLcEE8APdXuA47FkDNyDm0WhqpPgrOjHkrpL%2FcW6h4OG5SGG%2B6qhL30wy28FPpPtC%2FYvADkgH9Jbg6NkFXPCKsrgZM42%2Fz0JZDgrunpVHxHbtxZOy8zgPqk%3D&PageNum=1&SortBy=PARID&SortDir=+asc&PageSize=1&hdTaxYear=&hdAction=Link&hdCriteria=price%7C1000000%7E2000000&hdCriteriaLov=&hdCriteriaTypes=N%7CN%7CC%7CC%7CC%7CN%7CC%7CC%7CN%7CD%7CN%7CN%7CC%7CC%7CC%7CN%7CN&hdLastState=1&hdReset=&hdName=&hdSelectedQuery=0&mode=&hdSearchType=ADVANCED&hdListType=&hdIndex=0&hdSelected=&hdCriteriaGroup=&hdCriterias=taxyr%7Cbathrooms%7Cbedrooms%7CClass%7Cluc%7Csfla%7Cnbhd%7Cowner%7Cprice%7Csalesdate%7Ccom_sf%7Cstories%7Cadrstr%7Cstyle%7Ctaxdist%7Cyr_com%7Cyr_buitl&hdSelectAllChecked=false&sCriteria=0&ctl01%24cal1=&ctl01%24cal1%24dateInput=&ctl01_cal1_dateInput_ClientState=%7B%22enabled%22%3Atrue%2C%22emptyMessage%22%3A%22%22%2C%22validationText%22%3A%22%22%2C%22valueAsString%22%3A%22%22%2C%22minDateStr%22%3A%221900-01-01-00-00-00%22%2C%22maxDateStr%22%3A%222099-12-31-00-00-00%22%2C%22lastSetTextBoxValue%22%3A%22%22%7D&ctl01_cal1_calendar_SD=%5B%5D&ctl01_cal1_calendar_AD=%5B%5B1900%2C1%2C1%5D%2C%5B2099%2C12%2C30%5D%2C%5B2022%2C5%2C1%5D%5D&ctl01_cal1_ClientState=%7B%22minDateStr%22%3A%221900-01-01-00-00-00%22%2C%22maxDateStr%22%3A%222099-12-31-00-00-00%22%7D&txtCrit=&ctl01%24cal2=&ctl01%24cal2%24dateInput=&ctl01_cal2_dateInput_ClientState=%7B%22enabled%22%3Atrue%2C%22emptyMessage%22%3A%22%22%2C%22validationText%22%3A%22%22%2C%22valueAsString%22%3A%22%22%2C%22minDateStr%22%3A%221900-01-01-00-00-00%22%2C%22maxDateStr%22%3A%222099-12-31-00-00-00%22%2C%22lastSetTextBoxValue%22%3A%22%22%7D&ctl01_cal2_calendar_SD=%5B%5D&ctl01_cal2_calendar_AD=%5B%5B1900%2C1%2C1%5D%2C%5B2099%2C12%2C30%5D%2C%5B2022%2C5%2C1%5D%5D&ctl01_cal2_ClientState=%7B%22minDateStr%22%3A%221900-01-01-00-00-00%22%2C%22maxDateStr%22%3A%222099-12-31-00-00-00%22%7D&txtCrit2=&selSortBy=PARID&selSortDir=+asc&searchOptions%24hdBeta=&hdLink=..%2FDatalets%2FDatalet.aspx%3FsIndex%3D0%26idx%3D1&AkaCfgResults%24hdPins=&ReportsListParIDs=' \
  --compressed
```

```python
import requests

cookies = {
    "ASP.NET_SessionId": "5zbmmioup1jtvyidmrllbk3y",
    "DISCLAIMER": "1",
}

params = {
    "mode": "advanced",
}

data = {
    "__VIEWSTATE": [
        "xp+U7xWIH/WkG8AjGBqENMMc/lJWzEPo8hVNxOMXvVHVE6DLDW15N7QUlsVAmirgwz3l8N9B2Bao8Krnu1WzlljJr5ULUpOe3FrjCr0ByGJxuYXs8KRohuPMS00PQpVIYnQdeOLaUsr7cm8i2qOmGqgXtLrYRe4PfHO1RezWXMmvuM6LhiA3kZ2SHixuAsXKJC7Y1V7D6j5Ym5magtFXe8GQIG/HSC8uhY6ciEpbHrpCEeDJsXtyuOmk93pBrnvk+nJsWidtubDTPFQSWKwo0J0tH5gvf9ePUjCrJOGKfDzBJ+Y03TPxmBFkDSwX+Lct3N+0gmmYifB9YaZakj1fG90TyuxhXgnmh1xBHTFqQE5ANNBXuBAlyikA6NfDIlg1NWQINT+iLSurkNHLMYpvOPiUT183D5ZYr0l5kMnHFly0ESEbqLyVCcxWOybiaCYiq4zS7/gFWhQ9n59d13y59oJHpyVhGvijTaTSvGaqalY9ZLrV11hiXGh1XQySbJX+t4ku/ioO5IaIYI93Pv8k163sRczbLoNijz5qRFVmtjrrLXAkrZHMZP6s6QBG67W1MSFEQF9Evn5heWX9PR/sfWa6jMeh3jP5u72TZteV8g4="
    ],
    "__VIEWSTATEGENERATOR": ["81E50120"],
    "__EVENTVALIDATION": [
        "JGlJpwTn+zu8GzcJc0cWEZ2W46/xFsJKpBB6bL0XdXJXlE35rX3XiuWLCIFtcxWKdEHUHnOOrPR0aNbsfhqF3DDQJFkV+Lb95S/gn8GigaiPWiB9kTgAR7Al8doUG5V8LLYbpzb9LbDEg3ogCxansImqtx9fEu7usd6IxJWukxLhUor43DuBIGoDXeFIkTCa2ZcPOvfRDulGfsDlI3losFm+SFFiaCan9JgvgBWCJGnctSEd+7K5dGNWootxCprge3JHMN2koEkUx+nHFh8WzcBiwC4uAoYzSgETGI8yImOqYoD4HlW3WC3XgqsWTMU5oC4ICrut5g6fbBl9Y78lMtk0z8tWVyl6KYAT61lzk39hnOjKqtIQDeXYIoBVdqDRarOiaaQD5wIZgc8aUy1wh6auyT3SvnMTLbhBmUF5xKhyczsCjHAON3zbyt2ITbY77QGWx3KCoFkDNW4hLZCmtWXUR5Jpr44UyFK0Gdqfd7v8CQfDi2FyG2pxbdwB3f21ckA0C0cNknAb+tONxXwwhzHz/Nmka7cuzALQgX41oQyVfW2bM/he5G4Lil1M55bCEytG93p3Vw9sx+HeXJb0kVcSh39Q00rLSYUiCM+d3N0op25g35PooLcEE8APdXuA47FkDNyDm0WhqpPgrOjHkrpL/cW6h4OG5SGG+6qhL30wy28FPpPtC/YvADkgH9Jbg6NkFXPCKsrgZM42/z0JZDgrunpVHxHbtxZOy8zgPqk="
    ],
    "PageNum": ["1"],
    "SortBy": ["PARID"],
    "SortDir": [" asc"],
    "PageSize": ["1"],
    "hdAction": ["Link"],
    "hdCriteria": ["price|1000000~2000000"],
    "hdCriteriaTypes": ["N|N|C|C|C|N|C|C|N|D|N|N|C|C|C|N|N"],
    "hdLastState": ["1"],
    "hdSelectedQuery": ["0"],
    "hdSearchType": ["ADVANCED"],
    "hdIndex": ["0"],
    "hdCriterias": [
        "taxyr|bathrooms|bedrooms|Class|luc|sfla|nbhd|owner|price|salesdate|com_sf|stories|adrstr|style|taxdist|yr_com|yr_buitl"
    ],
    "hdSelectAllChecked": ["false"],
    "sCriteria": ["0"],
    "selSortBy": ["PARID"],
    "selSortDir": [" asc"],
    "hdLink": ["../Datalets/Datalet.aspx?sIndex=0&idx=1"],
}

response = requests.post(
    "https://publicaccess.claytoncountyga.gov/search/advancedsearch.aspx",
    params=params,
    cookies=cookies,
    data=data,
)

print(response)
print(response.text)

assert "LGS HOLDING GROUP 2013 LLC" in response.text
```

WRITEME: developing Scrapy project

```
$ scrapy startproject aspnetlegacy .
$ scrapy genspider clayton publicaccess.claytoncountyga.gov
```

WRITEME: final thoughts + recommendation to use Selenium/Playwright as fallback

