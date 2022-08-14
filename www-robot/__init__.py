"""\
www-robot - A basic WWW Robot for Python

www-robot is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version
3 of the License, or (at your option) any later version.\
"""

import urllib.robotparser
import urllib.request
import urllib.parse
import bs4
import sys

#	www-robot - A basic WWW Robot for Python
#
#	www-robot is free software: you can redistribute it and/or
#	modify it under the terms of the GNU General Public License
#	as published by the Free Software Foundation, either version
#	3 of the License, or (at your option) any later version.
#
#	www-robot is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty
#	of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#	See the GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public
#	License along with www-robot. If not, see
#	<https://www.gnu.org/licenses/>.

class PageResults:
	def __init__(self, useragent, url):
		self.useragent = useragent
		self.title = self.url = url
		self.description = "unknown"
		self.language = "unknown"
		self.responsive = False
		self.links = []
		self.keywords = []
		self.images = []

	def xml_str(self):
		return \
			f"<page><title>{self.title}</title>" + \
			f"<url>{self.url}</url>" + \
			f"<desc>{self.description}</desc>" + \
			f"<lang>{self.language}</lang>" + \
			f"<responsive>{'yes' if self.responsive else 'no'}</responsive>" + \
			f"<links>{''.join([str(link) for link in self.links])}</links>" + \
			f"<keywords>{''.join(['<keyword>' + str(keyword) + '</keyword>' for keyword in self.keywords])}</keywords>" + \
			f"<images>{''.join(['<image>' + str(image) + '</image>' for image in self.images])}</images></page>"

	__str__ = xml_str # XML by default

class Link:
	def __init__(self, url, text):
		self.url = url
		self.text = text

	def xml_str(self):
		return \
			f"<link><url>{self.url}</url><text>{self.text}</text></link>"

	__str__ = xml_str # XML by default


def analyze_page(url, robot):
	res = PageResults(robot, url)
	headers = {
		'User-Agent': robot,
		'Accept': '*',
	}
	req = urllib.request.Request(url, headers=headers)
	try:
		with urllib.request.urlopen(req) as f:
			html = f.read()
	except urllib.error.HTTPError as e:
		html = e.msg # no one asked about the page's opinion
	soup = bs4.BeautifulSoup(html, 'html.parser')
	if soup.title is not None:
		res.title = soup.title.string.strip()
	if soup.find('meta', {'name': 'description'}) is not None and soup.find('meta', {'name': 'description'}).get('content') is not None:
		res.description = soup.find('meta', {'name': 'description'})['content']
	if soup.find('html') is not None and soup.find('html').get('lang') is not None:
		res.language = soup.find('html')['lang']
	if soup.find('meta', {'name': 'viewport'}) is not None:
		res.responsive = True
	for link in soup.find_all('a'):
		if link.get('href') is not None:
			res.links.append(Link(link.get('href'), link.text))
	for keywordtag in soup.find_all('meta', {'name': 'keywords'}):
		if keywordtag.get('content') is not None:
			res.keywords.append([x.strip()
								for x in keywordtag.get('content').split(',')])
	for image in soup.find_all('img'):
		if image.get('src') is not None:
			res.images.append(image.get('src'))
	return res

analyzed = []
refs = {}

def deep_analyze_page(rp, url, robot):
	print(f"Analyzing {url}")
	res = analyze_page(url, robot)
	i = 0
	for link in res.links:
		if "://" in link.url and not link.url.replace("https://", "http://").startswith(url.replace("https://", "http://")):
			print(f"Skipping {i+1}/{len(res.links)}: {link.url}")
			i += 1
			if not link.url in refs:
				refs[link.url] = 1
			else:
				refs[link.url] += 1
			continue
		theurl = link.url
		if theurl.replace("https://", "http://").startswith(url.replace("https://", "http://")):
			theurl = theurl.replace("https://", "http://").replace(url.replace("https://", "http://"), "")
		elif not theurl.startswith("/"):
			theurl = url + "/" + theurl
		else:
			theurl = url.split("/")[0] + "//" + url.split("/")[2] + theurl

		if theurl in analyzed:
			res.links[i].url = theurl
			i += 1
			continue

		analyzed.append(theurl)

		if rp.can_fetch(robot, theurl):
			res.links[i] = deep_analyze_page(rp, theurl, robot)
		else:
			print(f"Skipping {i+1}/{len(res.links)}: {link.url}")
		i += 1
	return res

def main(url, robot):
	if not url.endswith("/"):
		url += "/"
	rp = urllib.robotparser.RobotFileParser()
	rp.set_url(url + "/robots.txt")
	headers = {
		'User-Agent': robot,
		'Accept': '*',
	}
	req = urllib.request.Request(url + "/robots.txt", headers=headers)
	try:
		with urllib.request.urlopen(req) as f:
			content = f.read()
		rp.parse(content.decode('utf-8').splitlines())
		if rp.can_fetch("ArtadoBot", "/"):
			results = deep_analyze_page(rp, url, robot)
			print("\n" + str(results))
	except:
		rp.parse(["User-Agent: *"])
		results = deep_analyze_page(rp, url, robot)
		print("\n" + "<analysis>" + str(results) + "<refs>" + "".join([("<ref><url>" + url + "</url><count>" + str(count) + "</count></ref>") for url, count in refs.items()]) + "</refs></analysis>")


if __name__ == "__main__":
	print(__doc__)
	sys.exit(0)
