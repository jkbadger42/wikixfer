import platform
from selenium import webdriver
import getpass
import time
import os

print('wikixfer: This utility will automatically open the Firefox browser,')
print('  go to the Mother wiki, log you in, and transfer the selected page')
print('  to the new wiki.')
print('')
print('MOVE THIS WINDOW TO THE LOWER-RIGHT CORNER OF THE SCREEN OR SOMEPLACE')
print('YOU CAN SEE IT WHEN THE BROWSER OPENS.')
print('')
myURL = input('Please enter the URL link of the MOTHER wiki page you want to transfer: ')
if myURL == '':
  myURL = 'https://wiki.keck.waisman.wisc.edu/wiki/projects/mother/'
r = myURL.rsplit('/', 1)[-1]
if r == '':
	r = myURL.rsplit('/', 1)[-2]
if '.html' in r:
	myWikiPageName = r.split('.', 1)[0]
else:
	myWikiPageName = r
myDir = os.getcwd() + os.sep + myWikiPageName
print('Creating directory "' + myDir + '"...')
os.makedirs(myDir, exist_ok=True)
os.chdir(myDir)
myUsername = getpass.getuser()
myPassword = getpass.getpass('Please enter your BI password: ')

print('Launching Firefox web browser...')
fp = webdriver.FirefoxProfile()
fp.set_preference('browser.download.folderList',2)
fp.set_preference('browser.download.dir', os.getcwd())
fp.set_preference('browser.download.manager.showWhenStarting', False)
#fp.set_preference("browser.download.manager.showWhenStarting", False);
#fp.set_preference("browser.download.manager.focusWhenStarting", False);  
#fp.set_preference("browser.download.useDownloadDir", True);
#fp.set_preference("browser.helperApps.alwaysAsk.force", False);
#fp.set_preference("browser.download.manager.alertOnEXEOpen", False);
#fp.set_preference("browser.download.manager.closeWhenDone", True);
#fp.set_preference("browser.download.manager.showAlertOnComplete", False);
#fp.set_preference("browser.download.manager.useWindow", False);
#fp.set_preference("services.sync.prefs.sync.browser.download.manager.showWhenStarting", False);
#fp.set_preference("pdfjs.disabled", True);
#fp.set_preference('browser.helperApps.neverAsk.saveToDisk', 'image/jpeg, image/jpg, image/png, application/octet-stream, application/pdf')

if platform.system() == 'Windows':
  from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
  binary = FirefoxBinary('C:/Program Files (x86)/Mozilla Firefox/firefox.exe')
  browser = webdriver.Firefox(firefox_binary=binary, firefox_profile=fp)
elif platform.system() == 'Darwin':
  print('Sorry! wikixfer only works under Windows and Linux!')
  exit()
else:
  browser = webdriver.Firefox(firefox_profile=fp)

print('Going to MOTHER wiki front page...')
# The login stuff only works reliably from the main MOTHER page, so go there first.
browser.get('https://wiki.keck.waisman.wisc.edu/wiki/projects/mother/')

print('Waiting for front page to complete loading...')
time.sleep(2)

print('Logging in to MOTHER wiki...')
id = browser.find_element_by_id('username')
pw = browser.find_element_by_id('password')
id.send_keys(myUsername)
pw.send_keys(myPassword)

button = browser.find_element_by_xpath("//input[@value='Log In']")
button.click()

print('Waiting for login to complete...')
time.sleep(4)

print('Going to your MOTHER wiki page "' + myURL + '" ...')
browser.get(myURL)

print('')
print('GO TO THE BROWSER WINDOW AND ADJUST THE WIKI PAGE IF NEED BE.')
print('For example, select an older version of the page that has what you want.')
print('')
blah = input('COME BACK TO THIS WINDOW AND PRESS ENTER WHEN READY: ')

print('Waiting for page rendering to complete....')
# This delay is very important, as a lot of Javascript runs on the page to complete
# the rendering of the wiki contents. Do the next call to get the outer HTML too soon,
# and you just get the generic Apple Wiki page 'wrapper' and not the user-entered
# content.
time.sleep(1)

fileName = myWikiPageName + '.html'
print('Saving wiki page source to "' + fileName + '"...')
body = browser.find_element_by_tag_name('body').get_attribute('outerHTML')
myHTML = body.encode('utf-8')
f = open(fileName, 'wb')
f.write(myHTML)
f.close()

# Images are tricky because of course they're displayed via
# JavaScript and aren't normal 'img' elements. So we can't just
# do a GET of the 'src' of the img. That triggers the JS call to
# save the image to disk, so we need to have the user help out
# by clicking the 'OK' button.
#
# Example img src URL:
# https://wiki.keck.waisman.wisc.edu/wiki/files/download/6f2b0c5e-62af-4793-8dde-629c9fe1505f

print('')
print('Getting images. You will need to save them.')
print('This will involve you switching between the browser')
print('window and this window.')
print('')
images = browser.find_elements_by_tag_name('img')
for i in images:
	imageSource = i.get_attribute('src')
	# There's one oddball image that's just a normal image, and
	# we don't want it. Worse, calling browser.get() basically
	# tells Firefox to display the image instead of the current
	# page. So skip it!
	if '.png' in imageSource:
		continue
	browser.get(imageSource)
	# Save dialog pops up, user saves file.
	blah = input('PRESS ENTER HERE WHEN IMAGE SAVED: ')

print('')
print('Handling downloadable files...')
downloads = browser.find_elements_by_class_name('left-cap')
for d in downloads:
	d.click()
	# Save dialog pops up, user saves file.
	blah = input('PRESS ENTER HERE WHEN FILE DOWNLOADED: ')

print('Closing Firefox...')
browser.quit()
