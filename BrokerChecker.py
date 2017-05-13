import json
import re
import urllib2
from bs4 import BeautifulSoup
import hashlib
import smtplib
import email

#               price           m2
patterns = [ur'[0-9]{3}', ur'[0-9]{2}']
matches = []
newmatches = []


# Send mail to notify the new match
def send_mail():
    messagestring = "Found " + str(len(newmatches)) + " new matches.\n"
    for match in newmatches:
        messagestring += "-------------------------------------------------\n"
        messagestring += "price: " + str(match[0]) + "\n"
        messagestring += "size: " + str(match[1]) + "\n"
        messagestring += "link: " + str(match[2]) + "\n\n"

    msg = email.message_from_string(messagestring)
    msg['From'] = "EMAILADDR"
    msg['To'] = "EMAILADDR"
    msg['Subject'] = "Found " + str(len(newmatches)) + " new matches."

    s = smtplib.SMTP("SMTPSERVER", 587)
    s.ehlo()  # Hostname to send for this command defaults to the fully qualified domain name of the local host.
    s.starttls()  # Puts connection to SMTP server in TLS mode
    s.ehlo()
    s.login('EMAILADDR', 'PASSWD')

    s.sendmail("EMAILADDR", "EMAILADDR", msg.as_string())

    s.quit()


# Write new match hash to file
def write_new_match(matchmd5):
    matchfile = open("matches", 'a')
    matchfile.write(matchmd5)
    matchfile.write("\n")
    matchfile.close()


# Check whether match has already been found once before by creating a md5 hash and comparing it to previous findings
def check_new_match():
    for match in matches:
        m = hashlib.md5()
        matchstring = match[0] + match[1] + match[2]
        m.update(matchstring)
        matchmd5 = m.hexdigest()
        new = True
        with open('matches', 'r') as matchfile:
            for line in matchfile:
                if matchmd5 in line:
                    new = False
        if new:
            write_new_match(matchmd5)
            newmatches.append(match)


# Check findings against criteria
def check_criteria(criteria, price, size, link):
    if int(criteria[0]) <= int(price) <= int(criteria[1]):  # Check price
        if int(size) >= int(criteria[2]):  # Check size
            match = [price, size, link]
            matches.append(match)


# Filter fields from posting to check and compare criteria
def check_requirements(postings, properties, criteria):
    for post in postings:
        pricestring = str(post.find_all("div", {"class": properties[3]})[0])
        price = re.findall(patterns[0], pricestring)[0]
        sizetring = str(post.find_all("div", {"class": properties[4]})[0])
        size = re.findall(patterns[1], pricestring)[0]
        linkstring = str(post.find_all("div", {"class": properties[5]})[0])
        link = linkstring[(linkstring.find('href="') + 6):]  # Cut leading string for link
        link = link[:link.find('"')]  # Cut tailing string off of link
        # If url is relative, add prefix
        if (properties[6] == True):
            link = properties[0] + link
        check_criteria(criteria, price, size, link)


# Find and split all postings on the page. url = url of the page containing the posts, classname = the class of the div tag
def get_postings(url, classname):
    page = urllib2.urlopen(url).read()
    soup = BeautifulSoup(page, "html.parser")
    postings = soup.find_all("div", {"class": classname})
    return postings


# Read properties from properties.json and start parsing and checking the postings
def read_properties():
    with open('properties.json') as data_file:
        data = json.load(data_file)
        for property in data["properties"]:
            islinkrelative = False
            if property["islinkrelative"] == "1":
                islinkrelative = True
            properties = [property["baseurl"], property["postingsurl"], property["postingdiv"],
                          property["pricedivclass"], property["sizedivclass"], property["linkdivclass"], islinkrelative]
            criteria = [data["criteria"]["minprice"], data["criteria"]["maxprice"], data["criteria"]["minsize"]]
            postings = get_postings(property["postingsurl"], property["postingdiv"])
            check_requirements(postings, properties, criteria)
    check_new_match()


read_properties()
send_mail()
print "Done! found " + str(len(newmatches)) + " new matches."

