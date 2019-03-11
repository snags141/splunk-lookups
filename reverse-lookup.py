#!/usr/bin/env python

import csv, sys, random, json, urllib2

""" 
    Date: 11/3/19
    Description: An adapter that takes CSV as input, performs a lookup to the operating
    system hostname resolution facilities, then returns the CSV results

"""

# Return a random user agent
def get_random_user_agent():
    chrome = ('Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
              'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36')
    firefox = ('Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) '
               'Gecko/20100101 Firefox/54.0',
               'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) '
               'Gecko/20150101 Firefox/47.0 (Chrome)')
    safari = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
              'AppleWebKit/601.7.7 (KHTML, like Gecko) '
              'Version/9.1.2 Safari/601.7.7',)
    user_agents = chrome + firefox + safari
    user_agent = random.choice(user_agents)
    return user_agent


# Return the http response
def get_http_response(url, ip):
    user_agent = get_random_user_agent()
    headers = {'User-Agent': user_agent}
    req = urllib2.Request(url, headers=headers)
    try:
        resp = urllib2.urlopen(req).read()
    except urllib2.URLError as ex:
        if hasattr(ex, 'reason'):
            print("%s - %s" % (ip, ex.reason))
            return None
        elif hasattr(ex, 'code'):
            print("%s - %s" % (ip, ex))
            return None
    return resp


# Get geolocation from "ip-api.com"
def get_geo_ipapi(ip):
    query_url = 'http://ip-api.com/json/' + ip.rstrip()
    resp = get_http_response(query_url, ip)
    if not resp:
        return None
    try:
        geo = json.loads(resp.decode('utf-8'))
    except (TypeError, ValueError):
        return None
    # Uses dict.get to set a default empty value if a key doesnt exists and to
    # avoid 'KeyError' exceptions
    location = {'country': geo.get('country', ''),
                'country_code': geo.get('countryCode', ''),
                'region': geo.get('regionName', ''),
                'region_code': geo.get('region', ''),
                'city': geo.get('city', ''),
                'isp': geo.get('isp', ''),
                'org': geo.get('org', '')
                }
    return location


# Set and return field values
def rlookup(ip):

    details = get_geo_ipapi(ip)

    if "country" in details:
        country = details["country"]

    if "country_code" in details:
        country_code = details["country_code"]

    if "region" in details:
        region = details["region"]

    if "region_code" in details:
        region_code = details["region_code"]

    if "city" in details:
        city = details["city"]

    if "isp" in details:
        isp = details["isp"]

    if "org" in details:
        org = details["org"]

    fields = [country, country_code, region, region_code, city, isp, org]
    return fields


def main():

    if len(sys.argv) != 9:
        print "Usage: python external_lookup.py [ip field]"
        sys.exit(1)

    ipfield = sys.argv[1]
    countryfield = sys.argv[2]
    country_codefield = sys.argv[3]
    regionfield = sys.argv[4]
    region_codefield = sys.argv[5]
    cityfield = sys.argv[6]
    ispfield = sys.argv[7]
    orgfield = sys.argv[8]

    infile = sys.stdin
    outfile = sys.stdout

    r = csv.DictReader(infile)
    header = r.fieldnames
    w = csv.DictWriter(outfile, fieldnames=r.fieldnames)
    w.writeheader()

    for result in r:
        # Perform the lookup
        #fields = rlookup('13.107.64.24')
        fields = rlookup(result[ipfield])
        result[countryfield] = fields["country"]
        result[country_codefield] = fields["country_code"]
        result[regionfield] = fields["region"]
        result[region_codefield] = fields["region_code"]
        result[cityfield] = fields["city"]
        result[ispfield] = fields["isp"]
        result[orgfield] = fields["org"]

        if result[countryfield] or result[country_codefield] or result[regionfield] or result[region_codefield] or result[cityfield] or result[ispfield] or result[orgfield]:
            w.writerow(result)


main()
