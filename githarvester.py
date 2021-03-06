#!/usr/bin/env python

# Import all the things!
import sys
try:
  import argparse
except:
  print '[!] argparse is not installed. Try "pip install argparse"'
  sys.exit(0)
try:
  from urllib import urlopen
except:
  print '[!] urllib is not installed. Try "pip install urllib"'
  sys.exit(0)
try:
  from bs4 import BeautifulSoup
except:
  print '[!] BeautifulSoup is not installed. Try "pip install beautifulsoup4"'
  sys.exit(0)
try:
  import re
except:
  print '[!] re is not installed. Try "pip install re"'
  sys.exit(0)

# Display Startup Banner
def banner():
  print ""
  print "  _____ _ _     _    _                           _"
  print " / ____(_) |   | |  | |                         | |"
  print "| |  __ _| |_  | |__| | __ _ _ ____   _____  ___| |_ ___ _ __ "
  print "| | |_ | | __| |  __  |/ _` | '__\ \ / / _ \/ __| __/ _ \ '__|"
  print "| |__| | | |_  | |  | | (_| | |   \ V /  __/\__ \ ||  __/ |   "
  print " \_____|_|\__| |_|  |_|\__,_|_|    \_/ \___||___/\__\___|_|   "
  print ""
  print "Version 0.5"
  print "By: @metacortex of @dc801"
  print ""

# Parse GitHub search results
def githubsearch(search, regex):
  navbarlinks = []
  searchurl = 'https://github.com/search?q=' + search + 'type=Code'
  print '[+] Searching Github for ' + search
  searchresults = urlopen(searchurl).read()
  soup = BeautifulSoup(searchresults, 'html.parser')

  # Find the bottom nav bar and parse out those links
  pagenav = soup.findAll('div', attrs={'class':'pagination'});
  for page in pagenav:
    pages = page.findAll('a')
    for a in pages:
      navbarlinks.append(a)
  totalpages = int(str(re.findall(r">.*</a>", str(navbarlinks[-2]))).strip('[').strip(']').strip('\'').strip('>').strip('</a>'))  # Because I suck at code
  print '  [+] Returned ' + str(totalpages) + ' total pages'

  # Parse each page of results
  currentpage = 1
  while (currentpage <= totalpages):
    parseresultpage(currentpage, search, regex)
    currentpage += 1

def parseresultpage(page, search, regex):
  print '    [+] Pulling results from page ' + str(page)
  pageurl = 'https://github.com/search?p=' + str(page) + '&q=' + search + '&type=Code'
  pagehtml = urlopen(pageurl).read()
  soup = BeautifulSoup(pagehtml, 'html.parser')

  # Find GitHub div with code results
  results = soup.findAll('div', attrs={'class':'code-list-item'})

  # Pull url's from results and hit each of them
  soup1 = BeautifulSoup(str(results), 'html.parser')
  for item in soup1.findAll('p', attrs={'class':'full-path'}):
    soup2 = BeautifulSoup(str(item), 'html.parser')
    for link in soup2.findAll('a'):
      individualresult = 'https://github.com' + str(link['href'])
      individualresultpage = urlopen(individualresult).read()
      soup3 = BeautifulSoup(str(individualresultpage), 'html.parser')
      for rawlink in soup3.findAll('a', attrs={'id':'raw-url'}):
        rawurl = 'https://github.com' + str(rawlink['href'])
        if (args.custom_regex) or (args.custom_search):
          searchcode(rawurl, regex)
        else:
          wpsearchcode(rawurl, regex)

def searchcode(url, regex):
  code = urlopen(url).read()
  result = ''
  try:
    regexresults = re.search(regex, str(code))
    result = str(regexresults.group(0))
    if (args.verbose == True):
      print "      [+] Found the following results"
      print "        " + result
    if args.write_file:
      if (result == ''):
        pass
      else:
        f = open(args.write_file, 'a')
        f.write(str(result + '\n'))
        f.close()
  except:
    pass

  if args.write_file:
    if (result == ''):
      pass
    else:
      f = open(args.write_file, 'a')
      f.write(str(result + '\n'))
      f.close()

#This whole function is confusing as hell FYI
def wpsearchcode(url, regex):
  code = urlopen(url).read()
  try:
    regexdb = re.search(r"define\(\'DB_NAME.*;", str(code), re.IGNORECASE)
    regexuser = re.search(r"define\(\'DB_USER.*;", str(code), re.IGNORECASE)
    regexpass = re.search(r"define\(\'DB_PASSWORD.*;", str(code), re.IGNORECASE)
    regexhost = re.search(r"define\(\'DB_HOST.*;", str(code), re.IGNORECASE)
    db = str(regexdb.group(0)).strip('define(\'').strip('\');').replace('\', \'', ':').strip('DB_NAME:')
    user = str(regexuser.group(0)).strip('define(\'').strip('\');').replace('\', \'', ':').strip('DB_USER:')
    password = str(regexpass.group(0)).strip('define(\'').strip('\');').replace('\', \'', ':').strip('DB_PASSWORD:')
    host = str(regexhost.group(0)).strip('define(\'').strip('\');').replace('\', \'', ':').strip('DB_HOST:')

    if (db == '\', '):  # Check for blank database because...shitty code
      db = ''
    if (user == '\', '):  # Check for blank user because...shitty code
      user = ''
    if (password == '\', '):  # Check for blank password because...shitty code
      password = ''
    if (host == '\', '):  # Check for blank host because...shitty code
      host = ''

    if (args.verbose == True):
      print '      [+] Found the following credentials'
      print '        database: ' + db
      print '        user: ' + user
      print '        password: ' + password
      print '        host: ' + host

    if args.write_file:
      f = open(args.write_file, 'a')
      results = 'Database: ' + db + '\nUser: ' + user + '\nPassword: ' + password + '\nHost: ' + host + '\n---\n'
      f.write(results)
      f.close()

  except:
    pass


def main():
  banner()  # Brandwhore

  # Parsing arguments
  parser = argparse.ArgumentParser(description='This tool is used for harvesting information from GitHub. By default it looks for code with the filename of \'wp-config.php\' and pulls out auth info')
  parser.add_argument('-r', action='store', dest='custom_regex', help='Custom regex string', type=str)
  parser.add_argument('-s', action='store', dest='custom_search', help='Custom GitHub search string', type=str)
  parser.add_argument('-v', '--verbose', action='store_true', help='Turn verbose output on')
  parser.add_argument('-w', action='store', dest='write_file', help='Write results to a file', type=str)
  global args
  args =  parser.parse_args()

  if args.custom_search:
    search = args.custom_search
    print '[+] Custom search is: ' + str(search)
  else:
    search = 'filename:wp-config.php'
    print '[+] Using default search'
  if args.custom_regex:
    regex = args.custom_regex
    print '[+] Custom regex is: ' + str(regex)
  else:
    regex = 'regexhere'
    print '[+] Using default regex'

  githubsearch(search, regex)

  print '[+] DONE'

if __name__ == "__main__":
  main()
