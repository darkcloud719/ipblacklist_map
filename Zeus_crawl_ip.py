import os,re,requests,hashlib,time,geoip2.database
from bs4 import BeautifulSoup
from datetime import datetime

NOW = datetime.now()
DB_PATH = "/root/py3_file/ipblocklist/GeoLite2-Country_20180206/GeoLite2-Country.mmdb"
reader = geoip2.database.Reader(DB_PATH)

def generate_iplist():
	with open('iplist.txt','r') as f:
		iplist = re.findall(r'[\d]+\.[\d]+\.[\d]+\.[\d]+',f.read())
		insert_ip_to_influxdb(iplist)

def insert_ip_to_influxdb(iplist):
	print(iplist)

	date = datetime.strftime(NOW,'%Y-%m-%d')
	year = datetime.strftime(NOW,'%Y')
	month = datetime.strftime(NOW,'%m')
	day = datetime.strftime(NOW,'%d')
	
	for ip in iplist:
		#timestamp = time.mktime(NOW.timetuple())
		#timestamp = int(timestamp)
		response = reader.country(ip)
		CMD = "curl -i -XPOST 'http://localhost:8086/write?db=mydb' --data-binary 'iplist,date={},year={},month={},day={},country={} ip=\"{}\"'".format(date,year,month,day,response.country.iso_code,ip)
		os.system(CMD)
	print("INSERT IPLIST COMPLETELY...")

def compare_md5(new_md5):
	with open('iplist_md5.txt','r') as f:
		old_md5 = f.read()
		if old_md5 == new_md5:
			return True
		else:
			return False

def write_new_md5(new_md5):
	with open('iplist_md5.txt','w') as f:
		f.write(new_md5)

def write_data(data):
	with open('iplist.txt','w') as f:
		f.write(data)

def crawler_ip(url):
	rs = requests.session()
	res = rs.get(url,verify=False)
	sp = BeautifulSoup(res.text,'html.parser')
	new_md5 = hashlib.md5(sp.text.encode('utf-8-sig')).hexdigest()
	if compare_md5(new_md5):
		print("NO UPDATE...")
		return False
	else:
		print("UPDATE...")
		write_new_md5(new_md5)
		write_data(sp.text)
		return True
	#with open('iplist.txt','w') as f:
	#	f.write(sp.text)


if __name__ == '__main__':
	url = "https://zeustracker.abuse.ch/blocklist.php?download=ipblocklist"
	if crawler_ip(url):
		generate_iplist()
	#print(iplist)
