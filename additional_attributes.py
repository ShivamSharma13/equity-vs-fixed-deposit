import requests
from bs4 import BeautifulSoup

def fetch_company_type(company_name, company_code):
	root_url = 'https://www.bseindia.com/SiteCache/1D/CompanyHeader.aspx?Type=EQ&text=' + company_code
	r = requests.get(root_url)
	soup = BeautifulSoup(r.content, 'html.parser')
	td_tags = soup.find_all('td')
	#hardcoded the below line. Can't find anything better right now.
	industry_type = td_tags[-1]
	company_name = company_name.replace('+' , ' ')
	write_string = company_name + ',' + company_code + ',' + industry_type.string + '\n'
	with open('data/company_type.csv', 'a') as file:
		file.write(write_string)


	