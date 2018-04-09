import requests
from bs4 import BeautifulSoup
import pprint
import re
import os

time_frame = 'M'

time_frame_params_M = {'DMY': 'rdbMonthly', 'cmbMonthly': '01', 'cmbMYear': '1995', 'hidDMY': 'M', 'hidFromDate': '01/01/1995', 'hidToDate': '04/09/2018'}
time_frame_params_Y = {'DMY': 'rdbYearly', 'cmbYearly': '1996', 'hidDMY': 'Y', 'hidFromDate' : '19960101', 'hidToDate': '20180409'}

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
							'ctl00$ContentPlaceHolder1$DDate' : '', 
							'ctl00$ContentPlaceHolder1$GetQuote1_smartSearch' : '', 
							'ctl00$ContentPlaceHolder1$GetQuote1_smartSearch2' : 'Enter+Security+Name+/+Code+/+ID', 
							'ctl00$ContentPlaceHolder1$hdflag' : '0', 
							'ctl00$ContentPlaceHolder1$hdnCode' : '',
							'ctl00$ContentPlaceHolder1$hidCompanyVal' : '', 
							'ctl00$ContentPlaceHolder1$hidCurrentDate' : '4/3/2018+12:00:00+AM', 
							'ctl00$ContentPlaceHolder1$Hidden1' : '', 
							'ctl00$ContentPlaceHolder1$Hidden2' : '',
							'ctl00$ContentPlaceHolder1$hiddenScripCode' : '', 
							'ctl00$ContentPlaceHolder1$hidOldDMY' : '', 
							'ctl00$ContentPlaceHolder1$hidYear' : '', 
							'ctl00$ContentPlaceHolder1$search' : 'rad_no1', 
							'myDestination' : '#',
						}

def if_retry_required():
	os.chdir('data')
	dir_files = os.listdir()
	if 'company_codes.txt' in dir_files:
		with open('company_codes.txt', 'r') as file:
			file_content = file.read()
			company_codes = file_content.split(' ')
		fetched_codes = []
		for file in dir_files:
			regex = re.search(r'[\d]{6}', str(file))
			if regex:
				indices = regex.span()
				fetched_codes.append(file[indices[0]:indices[1]])
		remaining_codes = []
		for company_code in company_codes:
			if (company_code not in fetched_codes) and (company_code != ''):
				remaining_codes.append(company_code)
		os.chdir('..')
		if not remaining_codes:
			print('Data already fetched.')
			exit()
		return remaining_codes
	else:
		os.chdir('..')
		False

def fetch_company_codes():
	'''
	The function picks up top 100 companies listed.
	'''
	url = 'https://www.bseindia.com/markets/equity/EQReports/TopMarketCapitalization.aspx'
	company_codes = []
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'html.parser')
	table_rows = soup.find_all('tr')
	for table_row in table_rows:
		filtered_table_rows = table_row.find_all('td', {'class' : 'TTRow_right'})
		for filtered_table_row in filtered_table_rows:
			if re.match(r'^[\d]{6}' , str(filtered_table_row.string)):
				company_codes.append(filtered_table_row.string)
	#print(company_codes)
	#print(len(company_codes))
	codes_in_str = ''
	for item in company_codes:	
		codes_in_str+=(item+' ')
	with open('data/company_codes.txt' , 'w') as file:
		file.write(codes_in_str)
	return company_codes


def update_payload(company_code):
	url = 'https://www.bseindia.com/SiteCache/90D/SmartGetQuoteData.aspx?Type=EQ&text='
	#company_code = '500238'
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

def _add_unnecessary_string(part_payload):
	unnecessary_string = 'ctl00$ContentPlaceHolder1$'
	'''
	This is a strange thing is happening. Apparently the data structure dict_keys([key1, key2, ...])
	is somewhat dynamic in nature during the execuiton of code. So the line,
	original_keys = part_payload.keys(), didn't work properly.
	After this line, the original_keys kept on changing during the execution of for loop. Hence, I supplied the unwinded list instead.
	'''
	original_keys = [*part_payload.keys()]
	for key in original_keys:
		new_key = unnecessary_string + key
		value = part_payload.pop(key)
		part_payload[new_key] = value
	

def _add_time_frame_payloads():
	'''
	Why global was used?
	Refer to: https://stackoverflow.com/questions/14323817/global-dictionaries-dont-need-keyword-global-to-modify-them/14323961#14323961
	and to, 
	link: https://stackoverflow.com/questions/3657163/how-to-reset-global-variable-in-python/3657214#3657214
	'''
	global desired_payload_keys
	if time_frame == 'M':
		_add_unnecessary_string(time_frame_params_M)
		desired_payload_keys = {**desired_payload_keys, **time_frame_params_M}
	if time_frame == 'Y':
		_add_unnecessary_string(time_frame_params_Y)
		desired_payload_keys = {**desired_payload_keys, **time_frame_params_Y}

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
	print("Website: True")
	return desired_payload_keys

def fetch_csv(url, payload, company_code, file_name_prefix):
	file_name = 'data/' + file_name_prefix + '_data_' + company_code + '.csv'
	try:
		r = requests.post(url , data = payload , headers = headers, stream = True)
	except requests.exceptions.NewConnectionError:
		print("Could not reach website. Company Code: " + company_code + " dropped.")
		return False
	with open(file_name , 'wb') as file:
		for chunk in r.iter_content(chunk_size = 128):
			file.write(chunk)
	return True

def main(url, file_name_prefix, retry_mode = False, remaining_codes = []):
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'html.parser')
	_add_time_frame_payloads()
	payload = gather_request_payload(soup)
	if remaining_codes:
		company_codes = remaining_codes
	else:
		company_codes = fetch_company_codes()
		print("Successfully fetched company codes...")
	failed_attempts_code = []
	for idx, company_code in enumerate(company_codes):
		if idx%5 == 0:
			print("Done " + str(idx) + '/' + str(len(company_codes)))
		update_payload(company_code)
		result = fetch_csv(url, payload, company_code, file_name_prefix)
		if not result:
			failed_attempts_code.append(company_code)
	if failed_attempts_code:
		print(str(len(failed_attempts_code)) + " hits were missed. Please Run the script again to fetch them.")
	else:
		print('Successfully collected data. Bye.')

if __name__ == "__main__":
	root_url = 'https://www.bseindia.com/markets/equity/EQReports/StockPrcHistori.aspx?expandable=7&flag=0'
	mode = input("Enter 'M' for monthly and 'Y' for yearly: ")
	if mode == 'Y':
		time_frame = 'Y'
		file_name_prefix = 'Y'
	elif mode == 'M':
		file_name_prefix = 'M'
	else:
		print('Wrong input, run the script agian.')
		exit()
	remaining_codes = if_retry_required()
	if remaining_codes:
		print('Previous files found, resuming scraping...')
		main(root_url, file_name_prefix, retry_mode = True, remaining_codes = remaining_codes)
	else:
		main(root_url, file_name_prefix)

