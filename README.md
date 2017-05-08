# BrokerChecker
While i was looking for a studio appartment i wanted to automate looking trough all the advertisements to find suitable appartments. This quick 'n dirty script as a result.

It works by scraping the HTML off a given page and filters posts with their prices, roomsizes and direct links. New websites can be added by adding a new object in the "properties" array in properties.json. One is filled in as an example. The fields need to be filled in as follows:
baseurl: URL of the homepage of the website, used as a prefix if href tags are relative
postingsurl: The URL on which all the postings are displayed.
postingdiv: Div tag that holds one post
pricedivclass: Div tag that holds the price per post
sizedivclass: Div tag that holds the room size per post
linkdivclass: Div tag that holds the URL per post
islinkrelative: Bool if the link is a relative (1) or direct (0) link.

The script will create a "matches" file. In there it will write hashes of already found and reported matches. It'll check this file to see if newly found matches are actually new to prevent spamming my mailbox.
