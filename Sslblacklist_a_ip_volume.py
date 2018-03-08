import os,re,requests,hashlib,time,datetime,geoip2.database
from bs4 import BeautifulSoup

SOURCE = "Ssl_aggresive"
DATE = datetime.date.today()
DB_PATH = "/root/py3_file/ipblocklist/GeoLite2-Country_20180206/GeoLite2-Country.mmdb"
reader = geoip2.database.Reader(DB_PATH)

def get_ssl_a_web_md5():
	url = "https://sslbl.abuse.ch/blacklist/sslipblacklist_aggressive.csv"
	rs = requests.session()
	res = rs.get(url,verify=False)
	sp = BeautifulSoup(res.text,'html.parser')
	new_md5 = hashlib.md5(sp.text.encode('utf-8-sig')).hexdigest()
	return new_md5,sp.text

def generate_ip_count():
	with open('Sslblacklist_a_ip_source.txt','r') as f:
		iplist = re.findall(r'[\d]+\.[\d]+\.[\d]+\.[\d]+',f.read())
		insert_ip_count_to_influxdb(iplist)

def insert_ip_count_to_influxdb(iplist):
	count = len(iplist)
	print(count)
	timestamp = time.mktime(DATE.timetuple())
	timestamp = int(timestamp)
	date = datetime.date.strftime(DATE,'%Y-%m-%d')
	print(date)
	CMD = "curl -i -XPOST 'http://localhost:8086/write?db=mydb&precision=s' --data-binary 'ssl_a_ip_count,date={} count={} {}'".format(date,count,timestamp)
	os.system(CMD)
	
	bounce = 1
	timestamp = int(time.time())
	for ip in iplist:
		timestamp+=bounce
		bounce+=1
		try:
			response = reader.country(ip)
		except:
			print('ERROR...')
		else:
			response = reader.country(ip)
			CMD_2 = "curl -i -XPOST 'http://localhost:8086/write?db=mydb&precision=s' --data-binary 'iplist,date={},country={},source={} ip=\"{}\" {}'".format(date,response.country.iso_code,SOURCE,ip,timestamp)
			os.system(CMD_2)
	print("INSERT IP COUNT COMPLETELY...")

def write_new_md5(new_md5):
	with open('Sslblacklist_a_ip_volume_md5.txt','w') as f:
		f.write(new_md5)

def write_new_data(new_data):
	with open('Sslblacklist_a_ip_source.txt','w') as f:
		f.write(new_data)

def compare_md5():
	new_md5,new_data = get_ssl_a_web_md5()
	with open('Sslblacklist_a_ip_volume_md5.txt','r') as f:
		old_md5 = f.read()
		if old_md5 == new_md5:
			return False
		else:
			write_new_md5(new_md5)
			write_new_data(new_data)
			return True

if __name__ == '__main__':
	if compare_md5():
		print("UPDATE...")
		generate_ip_count()
	else:
		print("NO UPDATE...")
