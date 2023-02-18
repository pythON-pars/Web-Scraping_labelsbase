import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
from fake_useragent import UserAgent

# Your cookies should be here
cookies = {
    '_ga': '********',
    '__gads': '********',
    '__gpi': '********',
    '_gid': '********',
    'remember_web_********': '********',
    'XSRF-TOKEN': '********',
    'labelsbase_session': '********',
    '_gat': '*',
}


def response(url):
    """
        Fake header request feature to avoid blocking
    """

    headers = {
        'user-agent':UserAgent()['google chrome']
    }
    
    res = requests.get(url, headers=headers, cookies=cookies)
    
    return res.text

def pars_page():
    """
        The page parsing function, after which it gives control to pars_user to collect user data. Actually, pars_user could be better, but it works
    """

    # start jobs with excel 
    wb = Workbook()

    sheet = wb.active
    
    # new title
    sheet.title = "sheet1"

    # column name
    sheet['A1'] = "Name"
    sheet['B1'] = "Genres"
    sheet['C1'] = "General contact"
    sheet['D1'] = "Demo email to A&R"
    sheet['E1'] = "Booking artists"
    sheet['F1'] = "Demo submission form"
    sheet['G1'] = "URL soundcloud"
    sheet['H1'] = "subscribers_soundcloud"
    sheet['I1'] = "URL labelsbase"

    # we run through the pages in a loop and add the data that comes from pars_user, having previously passed the necessary data to it
    c = 1
    for i in range(0, 391 + 1):
        
        # page output
        print(f"{i}/{i-391}")
        
        headers = {
            'user-agent':UserAgent()['google chrome']
        }

        res = requests.get(f"https://labelsbase.net/?page={i}", headers=headers, cookies=cookies)
        soup = BeautifulSoup(res.text, 'lxml')

        # here we take the link to the profile for further parsing
        urlsTarget = soup.find_all('div', class_='label-card-head-flex')
        for item in urlsTarget:
            c+=1
            try:
                user_name, genres_result, general, demo, booking, submission, soundcloud, subscribers_soundcloud = pars_user(response(item.find('a').get('href')), count=c)
            except Exception:
                continue
                
            sheet[f'A{c}'] = user_name
            sheet[f'B{c}'] = ', '.join(genres_result)
            sheet[f'C{c}'] = general
            sheet[f'D{c}'] = demo
            sheet[f'E{c}'] = booking
            sheet[f'F{c}'] = submission
            sheet[f'G{c}'] = soundcloud
            try:
                sheet[f'H{c}'] = subscribers_soundcloud.replace(',', '') # this is to get just some number, without a comma (without float )
            except:
                continue
            sheet[f'I{c}'] = item.find('a').get('href')
        
        print(f"Line: {c}") # output Line
        
    # save data in excel
    wb.save('balances.xlsx')

def pars_user(src, count):
    """
        src - Here you need to pass html markup
        count - seems redundant)
    """

    soup = BeautifulSoup(src, 'lxml')
    user_name = soup.find('h1', class_='label-name').text.strip()
    
    # I set the value to all names at once - it seemed to me correct / simple
    general = "None"
    demo = "None"
    booking = "None"
    submission = 'None'
    soundcloud = 'None'
    subscribers_soundcloud = 'None'
    genres_result = []

    # this list just lists some values ​​from user pages, at first 
    # I thought about collecting data in some other way, but in the end I came to this conclusion, but it works as it should
    dig = ['Techno', 'Tech House', 'Deep House', 'House', 'Progressive House', 'Electronica', 'Electro House', 'Minimal', 'Trance', 'Dance', 'Future House', 'Big Room', 'Dubstep', 'Pop', 'Chill Out', 'Hip-Hop', 'Nu Disco', 'Indie Dance', 'Hard Techno', 'Drum & Bass', 'Psy-Trance', 'Breaks', 'Rock', 'Hard Dance', 'Afro House', 'Downtempo', 'Ambient', 'Trap', 'Hardcore', 'Future Bass', 'Indie Rock', 'Reggae', 'Glitch Hop', 'Metal', 'Synthwave', 'Punk', 'Hard Rock', 'Pop Punk'] 
    try:
        genres = soup.find('div', class_='col-md-6').find_all('a')
        for i in genres:
            for item in dig:
                if item == i.text:
                    genres_result.append(i.text)

        # We collect all the necessary addresses
        block = soup.find('div', class_='col-md-6')
        count = 0
        for i in block.text.strip().split('Contacts')[-1].split('Links in web')[0].split('\n'):
            count += 1

            if i == '                                                    General contact:':
                general = block.text.strip().split('Contacts')[-1].split('Links in web')[0].split('\n')[count]
                if general == '':
                    continue
            if i == '                                                    Demo email to A&R:':
                demo = block.text.strip().split('Contacts')[-1].split('Links in web')[0].split('\n')[count]
                if demo == '':
                    continue
            if i == '                                                    Booking artists:':
                booking = block.text.strip().split('Contacts')[-1].split('Links in web')[0].split('\n')[count]
                if booking == '':
                    continue
            if i == "                                                    Demo submission form:":
                submission = block.text.strip().split('Contacts')[-1].split('Links in web')[0].split('\n')[count]
                if booking == '':
                    continue
        
        for i in block.find_all('a'):
            try:
                if i.get('href').split('/')[2].strip() == "soundcloud.com":
                    soundcloud = i.get('href')
            except Exception as ex:
                continue
                
        try:
            subscribers_soundcloud = soup.find('span', class_='text-muted pull-right').text.strip()
        except:
            subscribers_soundcloud = 'None'

    except AttributeError: 
        # The exception here is for the fact that not all pages are the same, 
        # so it was decided in case of an exception to choose a different processing path - it works as it should)
        
        bias = soup.find('div', class_='block-content').find_all('a')
        for i in bias:
            for item in dig:
                if item == i.text:
                    genres_result.append(i.text)
        
        block = soup.find('div', class_='block-content')
        count = 0
        for i in block.text.strip().split('Contacts')[-1].split('Links in web')[0].split('\n'):
            count += 1
            
            if i == '                                    General contact:':
                general = block.text.strip().split('Contacts')[-1].split('Links in web')[0].split('\n')[count]
                if general == '':
                    continue
            if i == '                                    Demo email to A&R:':
                demo = block.text.strip().split('Contacts')[-1].split('Links in web')[0].split('\n')[count]
                if demo == '':
                    continue
            if i == '                                    Booking artists:':
                booking = block.text.strip().split('Contacts')[-1].split('Links in web')[0].split('\n')[count]
                if booking == '':
                    continue
            if i == "                                    Demo submission form:":
                submission = block.text.strip().split('Contacts')[-1].split('Links in web')[0].split('\n')[count]
                if submission == '':
                    continue
        for i in bias:
            try:
                if i.get('href').split('/')[2].strip() == "soundcloud.com":
                    soundcloud = i.get('href')
            except:
                continue

        try:
            subscribers_soundcloud = soup.find('span', class_='text-muted pull-right').text.strip()
        except:
            subscribers_soundcloud = 'None'

    return user_name, genres_result, general, demo, booking, submission, soundcloud, subscribers_soundcloud

def main():
    pars_page()

if __name__ == '__main__':
    main()
