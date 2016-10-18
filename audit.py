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
	write_to_html(url, "Number of empty alt tags", number_of_empty_alt)
	
	# Find links without titles
	number_of_empty_title=0
	for link in soup.find_all("a"):
		title_of_link=link.get('title', '')
		
		if "title" not in title_of_link:
			number_of_empty_title=number_of_empty_title+1
			
	print "Number of <a> tags without titles is %d" % number_of_empty_title
	write_to_html(url, "Number of a tags without titles is", number_of_empty_title)

	# Find link tags with no titles
	number_of_empty_title=0
	for link_tag in soup.find_all("link"):
		title_of_link=link.get('title', '')
		
		if "title" not in title_of_link:
			number_of_empty_title=number_of_empty_title+1
			
	print "Number of <link> tags without titles is %d" % number_of_empty_title	
	write_to_html(url, "Number of link tags without titles is ", number_of_empty_title)

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
		write_to_html(url, "W3C Error ", error)
	index=0
	for item in response_soup.find_all('li', class_="warning"):
		index=index+1
		if len(item)<1:
			print "no warning"
			break
		else:
			warning=cleanhtml(str(item))
			print "Warning # %d is: %s" % (index, warning)
			write_to_html(url, "W3C Warning ", warning)
	
	# Find the inline css js
	script = soup.find('script')
	if len(script) > 0:
		print "Inline CSS/JS detected"
		write_to_html(url, "Inline CSS JS", "Yes")


	#TO-DO Find Pagespeed Ranking
	#test_url="https://www.googleapis.com/pagespeedonline/v2/runPagespeed?url="+url+"&key=AIzaSyCVUvnUHExB-i--Tx_Ug9K27iDnPpnqCK8&strategy=desktop"
	#page_speed_response=requests.get(test_url)
	#print page_speed_response.text
	#page_speed_data=json.loads(page_speed_response.text)
	#page_speed_data=page_speed_response.json()
	#print "the page speed score is ", page_speed_data["SPEED"]
	


def create_html_report():
	outfile = open("output.html", "w")
	print >>outfile, """<html>
		<head>
 		<title>Front End Audit Report</title>
		</head>
		<body>
		<table border="1">"""
	print >>outfile, "<tr><th>URL</th><th>Check for</th><th>Result</th></tr>"

def write_to_html(url, check, result):
	outfile=open("output.html", "a")
	print >>outfile, "<tr><td>"+url+"</td><td>"+check+"</td><td>"+str(result)+"</td></tr>"


try:

	if len(sys.argv) < 1:
		print "insufficient arguments"
		die

	filename=str(sys.argv[1])
	print filename

	create_html_report()

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

except Exception, e:
	print "Failed to read csv file: %s" % e





