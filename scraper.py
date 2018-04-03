import requests
from bs4 import BeautifulSoup
import pprint

headers = { 'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0'}

dynamic_payload = ['__VIEWSTATE',
					'__VIEWSTATEGENERATOR',
					'__EVENTVALIDATION',
					'WINDOW_NAMER', 
					'ctl00$ContentPlaceHolder1$hidCurrentDate',
					]

desired_payload_keys = {'__VIEWSTATE' : '' ,
							'__VIEWSTATEGENERATOR' : '', 
							'__EVENTVALIDATION' : '',
							'WINDOW_NAMER' : '', 
							'ctl00$ContentPlaceHolder1$btnSubmit.x' : '43', 
							'ctl00$ContentPlaceHolder1$btnSubmit.y' : '14',
							'ctl00$ContentPlaceHolder1$cmbYearly' : '2001', 
							'ctl00$ContentPlaceHolder1$DDate' : '', 
							'ctl00$ContentPlaceHolder1$DMY' : 'rdbYearly',
							'ctl00$ContentPlaceHolder1$GetQuote1_smartSearch' : 'WHIRLPOOL+OF+INDIA+LTD', 
							'ctl00$ContentPlaceHolder1$GetQuote1_smartSearch2' : 'Enter+Security+Name+/+Code+/+ID', 
							'ctl00$ContentPlaceHolder1$hdflag' : '0', 
							'ctl00$ContentPlaceHolder1$hdnCode' : '500238',
							'ctl00$ContentPlaceHolder1$hidCompanyVal' : 'WHIRLPOOL', 
							'ctl00$ContentPlaceHolder1$hidCurrentDate' : '4/3/2018+12:00:00+AM', 
							'ctl00$ContentPlaceHolder1$Hidden1' : '', 
							'ctl00$ContentPlaceHolder1$Hidden2' : '',
							'ctl00$ContentPlaceHolder1$hiddenScripCode' : '500238', 
							'ctl00$ContentPlaceHolder1$hidDMY' : 'Y', 
							'ctl00$ContentPlaceHolder1$hidFromDate' : '20000101', 
							'ctl00$ContentPlaceHolder1$hidOldDMY' : '', 
							'ctl00$ContentPlaceHolder1$hidToDate' : '20180403', 
							'ctl00$ContentPlaceHolder1$hidYear' : '', 
							'ctl00$ContentPlaceHolder1$search' : 'rad_no1', 
							'myDestination' : '#',
						}

def hit(url):
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'html.parser')
	payload = gather_request_payload(soup)
	r = requests.post(url , data = payload , headers = headers, stream = True)
	print(r.status_code)
	# print(r.content) : Recieved desired html page here.


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
			if (key in desired_payload_keys) and (key in dynamic_payload):
				desired_payload_keys[key] = value.replace(' ' , '+')
			else:
				pass
	return desired_payload_keys



if __name__ == "__main__":
	url = 'https://www.bseindia.com/markets/equity/EQReports/StockPrcHistori.aspx?expandable=14&flag=0'
	hit(url)



