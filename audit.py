import csv
import sys
import urllib2
import requests
from bs4 import BeautifulSoup
import urllib
import urllib2
import re
import html
import json
import re
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import js2py


def cleanhtml(raw_html):
	TAG_RE = re.compile(r'<[^>]+>')
	cleantext=TAG_RE.sub('', raw_html)
	return cleantext

def scan_page_source(url):
	response=requests.get(url)
	data=response.text
	soup = BeautifulSoup(data, "html.parser")
	
	#find all img tags
	number_img_tag=len(soup.find_all("img"))
	print number_img_tag

	#Find all img tags with blank alt atributes
	number_of_empty_alt=0
	
	for tag in soup.find_all("img"):
		alt_tag=tag.get('alt', '')
		#print alt_tag
		if not alt_tag:
			number_of_empty_alt=number_of_empty_alt+1
	print "Number of empty alt tags is %d" % number_of_empty_alt	 
	write_to_html("Number of empty alt tags", number_of_empty_alt)
	
	# Find links without titles
	number_of_empty_title=0
	for link in soup.find_all("a"):
		title_of_link=link.get('title', '')
		
		if "title" not in title_of_link:
			number_of_empty_title=number_of_empty_title+1
			
	print "Number of <a> tags without titles is %d" % number_of_empty_title
	write_to_html("Number of a tags without titles is", number_of_empty_title)

	# Find link tags with no titles
	number_of_empty_title=0
	for link_tag in soup.find_all("link"):
		title_of_link=link.get('title', '')
		
		if "title" not in title_of_link:
			number_of_empty_title=number_of_empty_title+1
			
	print "Number of <link> tags without titles is %d" % number_of_empty_title	
	write_to_html("Number of link tags without titles is ", number_of_empty_title)

	# Find the w3c errors and warnings

	URL = "https://validator.w3.org/nu/?doc="
	print URL
	SITE_URL = url
	request = URL+SITE_URL
	print request
	
	w3c_response = requests.get(request)
	response_data=w3c_response.text

	response_soup = BeautifulSoup(response_data, "html.parser")

	index=0
	for item in response_soup.find_all('li', class_="error"):
		index=index+1
		error=cleanhtml(str(item))
		#print error
		print "Error # %d is: %s" % (index, error)
		write_to_html("W3C Error ", error)
	index=0
	for item in response_soup.find_all('li', class_="warning"):
		index=index+1
		if len(item)<1:
			print "no warning"
			break
		else:
			warning=cleanhtml(str(item))
			print "Warning # %d is: %s" % (index, warning)
			write_to_html("W3C Warning ", warning)
	
	# Find the inline css js
	script_tag = soup.find_all('script')
	if len(script_tag) > 0:
		print "Inline CSS/JS detected"
		write_to_html("Occurences of Inline CSS JS  ", len(script_tag))

	count=0
	for link in soup.find_all('script'):
		count=count+1
	print "script tags number is ",count

	# Find dead code
	#pattern=re.compile("<!--(?!<!)[^\[>].*?-->")
	count=0
	pattern=r"<!--(.*?)-->"
	#matches=pattern.match(data)
	
	matches = re.findall(pattern, data)
	
	#matches = re.finditer(pattern, data)
	for match in matches:
		if ("IE" not in match):
			count=count+1
			#print "dead code found "
	print "dead code /inline comments (excluding IE directives) is ", count
	write_to_html("Dead code/ comments (excluding IE directives)", count)


	#FIND console errors
	
	driver = webdriver.PhantomJS()
	driver.get(url)
	i=1
	for entry in driver.get_log('browser'):
		print "Browser log %d is %s" %(i ,entry)
		write_to_html("Console error %d" % i,  entry)
		i=i+1



	#Get tab index on page
	count=0
	pattern=r"<(.*?)tabindex(.*?)>"
	#matches=pattern.match(data)
	
	matches = re.findall(pattern, data)
	
	#matches = re.finditer(pattern, data)
	for match in matches:
		count=count+1
	print "Number of tab Index occurences is ", count
	write_to_html("Number of tab Index occurences", count)


	#Detect empty tags
	count=0
	pattern = r"/<[^\/>][^>]*><\/[^>]+>/"
	#pattern=r"document"
	matches = re.findall(pattern, data)
	
	#matches = re.finditer(pattern, data)
	for match in matches:
		count=count+1
	print "Number of empty tags occurences is ", count
	write_to_html("Number of  empty tag  occurences", count)

	#Detect import statements in CSS files
	# Find all external style sheet references
	ext_styles = soup.findAll('link', rel="stylesheet")
	# Find all internal styles
	int_styles = soup.findAll('style')
	int_found = 0
	if (len(int_styles) != 0):
		print "Found %d internal stylesheet" % len(int_styles)
		for i in int_styles:
			if ("import" in i):
				int_found=int_found+1
				print "import statement present"
		write_to_html("Number of  import tag in internal stylesheet ", int_found)
	else:
		print "No internal stylesheets found"

	ext_found=0
	if (len(ext_styles) != 0):
		print "Found %d external stylesheet" % len(ext_styles)
		for i in ext_styles:
			if ("import" in i):
				ext_found=ext_found+1
				print "import statement present in external stylesheet"
		write_to_html("Number of  import tag in external stylesheet ", ext_found)
	else:
		int_found = 0
		print "No external stylesheets found"
	


	#TO-DO Find Pagespeed Ranking
	#test_url="https://www.googleapis.com/pagespeedonline/v2/runPagespeed?url="+url+"&key=AIzaSyCVUvnUHExB-i--Tx_Ug9K27iDnPpnqCK8&strategy=desktop"
	#page_speed_response=requests.get(test_url)
	#print page_speed_response.text
	#page_speed_data=json.loads(page_speed_response.text)
	#page_speed_data=page_speed_response.json()
	#print "the page speed score is ", page_speed_data["SPEED"]
	


def create_html_report(url=None):
	if url is None:
		outfile = open("output.html", "w")
		print >>outfile, """<html>
			<head>
 			<title>Front End Audit Report</title>
			</head>
			<body>
			<table border="1">"""
		print >>outfile, "<tr><th>URL</th><th>Check for</th><th>Result</th></tr>"
	else:
		outfile = open("output.html", "w")
		print >>outfile, """<html>
			<head>
 			<title>Front End Audit Report </title>
			</head>
			<body>
			<p><h1>Audit results  for {url}</h1>
			<table border="1">""".format(url=url)
		print >>outfile, "<th>Check for</th><th>Result</th></tr>"


def write_to_html(check, result, url=None):
	if url is None:
		outfile=open("output.html", "a")
		print >>outfile, "<tr><td>"+check+"</td><td>"+str(result)+"</td></tr>"




def read_csv(filename):
	
	row_count = len(open(filename).readlines())
	print "Number of URLs to scan are ", row_count
	if row_count < 1 or row_count > 10:
		print "empty or too large file"
		die
	
	index=0
	url_list =[]

	for line in open(filename):
	    csv_row = str(line.split())
	    url_list.append(str(csv_row))

	print str(url_list[0])
	    
	while index <row_count:
		print "Url %d  to consider for audit is: %s" % (index, url_list[index])
		scan_page_source(url_list[index].replace("'", "").replace("[", "").replace("]", ""))
		index=index+1


try:

	if len(sys.argv) < 1:
		print "insufficient arguments"
		die

	filename=str(sys.argv[1])
	print filename
	create_html_report()
	if(".csv" not in filename):
		if ("http" not in filename):
			filename="http://"+filename
		create_html_report(filename)
		scan_page_source(filename)
	else:
		read_csv(filename)

	

	

except Exception, e:
	print "Failed to read csv file: %s" % e





