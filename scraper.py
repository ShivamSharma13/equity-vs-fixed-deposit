import requests
from bs4 import BeautifulSoup
import pprint

headers = { 'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0'}

payload_from_html = ['__VIEWSTATE',
					'__VIEWSTATEGENERATOR',
					'__EVENTVALIDATION',
					'WINDOW_NAMER', 
					'ctl00$ContentPlaceHolder1$hidCurrentDate',
					]

desired_payload_keys = {'__VIEWSTATE' : '' ,
							'__VIEWSTATEGENERATOR' : '', 
							'__EVENTVALIDATION' : '',
							'WINDOW_NAMER' : '', 
							'ctl00$ContentPlaceHolder1$btnDownload.x' : '43', 
							'ctl00$ContentPlaceHolder1$btnDownload.y' : '14',
							'ctl00$ContentPlaceHolder1$cmbYearly' : '2001', 
							'ctl00$ContentPlaceHolder1$DDate' : '', 
							'ctl00$ContentPlaceHolder1$DMY' : 'rdbYearly',
							'ctl00$ContentPlaceHolder1$GetQuote1_smartSearch' : '', 
							'ctl00$ContentPlaceHolder1$GetQuote1_smartSearch2' : 'Enter+Security+Name+/+Code+/+ID', 
							'ctl00$ContentPlaceHolder1$hdflag' : '0', 
							'ctl00$ContentPlaceHolder1$hdnCode' : '',
							'ctl00$ContentPlaceHolder1$hidCompanyVal' : '', 
							'ctl00$ContentPlaceHolder1$hidCurrentDate' : '4/3/2018+12:00:00+AM', 
							'ctl00$ContentPlaceHolder1$Hidden1' : '', 
							'ctl00$ContentPlaceHolder1$Hidden2' : '',
							'ctl00$ContentPlaceHolder1$hiddenScripCode' : '', 
							'ctl00$ContentPlaceHolder1$hidDMY' : 'Y', 
							'ctl00$ContentPlaceHolder1$hidFromDate' : '20000101', 
							'ctl00$ContentPlaceHolder1$hidOldDMY' : '', 
							'ctl00$ContentPlaceHolder1$hidToDate' : '20180403', 
							'ctl00$ContentPlaceHolder1$hidYear' : '', 
							'ctl00$ContentPlaceHolder1$search' : 'rad_no1', 
							'myDestination' : '#',
						}

def fetch_formatted_name(company_code):
	url = 'https://www.bseindia.com/SiteCache/90D/SmartGetQuoteData.aspx?Type=EQ&text='
	company_code = '500238'
	r = requests.get(url+company_code)
	soup = BeautifulSoup(r.content, 'html.parser')
	anchors = soup.find_all('a')
	text_raw = anchors[0].get_text()
	#expected text_raw = WHIRLPOOL OF INDIA LTD|WHIRLPOOL|500238
	names = text_raw.split('|')
	company_name = names[0].replace(' ', '+')
	hidCompanyVal = names[1]
	#print(company_name)
	desired_payload_keys['ctl00$ContentPlaceHolder1$GetQuote1_smartSearch'] = company_name
	desired_payload_keys['ctl00$ContentPlaceHolder1$hidCompanyVal'] = hidCompanyVal
	desired_payload_keys['ctl00$ContentPlaceHolder1$hdnCode'] = company_code
	desired_payload_keys['ctl00$ContentPlaceHolder1$hiddenScripCode'] = company_code



def gather_request_payload(soup):
	input_tags = soup.find_all('input')
	filtered_tags = list()
	for input_tag in input_tags:
		try:
			name = input_tag.attrs['name']
			value = input_tag.attrs['value']
			filtered_tags.append({name : value})
		except KeyError:
			pass
	for filtered_tag in filtered_tags:
		for key, value in filtered_tag.items():
			if (key in desired_payload_keys) and (key in payload_from_html):
				desired_payload_keys[key] = value.replace(' ' , '+')
			else:
				pass
	return desired_payload_keys

def hit(url):
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'html.parser')
	payload = gather_request_payload(soup)
	fetch_formatted_name(34)
	r = requests.post(url , data = payload , headers = headers, stream = True)
	with open('data.csv' , 'wb') as file:
		for chunk in r.iter_content(chunk_size = 128):
			file.write(chunk)

if __name__ == "__main__":
	url = 'https://www.bseindia.com/markets/equity/EQReports/StockPrcHistori.aspx?expandable=14&flag=0'
	hit(url)



