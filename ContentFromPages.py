import os
import urllib.request
from bs4 import BeautifulSoup
from bs4.element import Comment
from tqdm import tqdm
import requests
import time
import re

class Deviations:
    def __init__(self, url, fav_count, view_count, comment_count):
        self.url = url
        self.fav_count = fav_count
        self.view_count = view_count
        self.comment_count = comment_count
        self.score = self.calculateScore()

    def getUrl(self):
        return self.url
    
    def getFavCount(self):
        return self.fav_count

    def getViewCount(self):
        return self.view_count

    def getCommentCount(self):
        return self.comment_count

    def getScore(self):
        return self.score

    def calculateScore(self):
        return self.view_count + self.fav_count * 20 + self.comment_count * 5


# Checks to see if a username triggers a 404 error from DA
# If so, user does not exist, and should return false
def usernameValidURL(url):
    reply = requests.get(url)
    if reply.status_code == 404:
        return False
    return True

def sortDeviationPageForMainImage(pageImages, urlToCompareAgainst):
    for page in pageImages:
        correctTerms = 0
        if "wixmp" in page.get('src'):
            # If len(titleTerms) is the same as correctTerms, then the image title is the same
            # and that means we've most likely found the image we're looking for.
            titleTerms = page.get('alt')
            titleTerms = re.split('[!@#$?\' _`\{\}^~|\\\,.:()\-+\[\]<>]', titleTerms)
            for term in titleTerms:
                # term = re.sub('[!@#$?\'.()-+]', '', term)
                if term in urlToCompareAgainst:
                    correctTerms += 1
            if correctTerms == len(titleTerms):
                return page.get('src')
            else:
                continue

    return None

def getFilesFromDAPages(username, listOfPages):


    #Make new folder with username
    cwd = os.getcwd()

    # Make Deviants folder for all artists to be stored
    # in if it doesn't exist already
    masterFolder = os.path.join(cwd, "Deviants")
    if not os.path.exists(masterFolder):
        os.mkdir(masterFolder)

    # Make folder for artist if it doesn't exist already
    newDir = os.path.join(masterFolder, username)
    if not os.path.exists(newDir):
        os.mkdir(newDir)


    #Go through all urls and get images
    for url in listOfPages:
        try:
            page = requests.get(url)

            soup = BeautifulSoup(page.content, 'html.parser')

            time.sleep(1)

            # text="Literature Text" means it is a story. Will need to add way to save these later.
            if soup.find_all('h2', text="Literature Text"):
                print("Story Found: "+url)
                continue
            # If there is a url in the return list, it's a mp4 video.
            elif soup.select("*[href*=mp4]"):
                tempList = soup.select("*[href*=mp4]")[0]
                image_url = tempList.get("href")
            #Else it is not MP4, and needs to be found as a normal video
            else:
                image_url = sortDeviationPageForMainImage(soup.find_all('img'), url)
                if image_url == None:
                    print("Image not found on page: "+url)
                    continue
                    

            # Splits the file name from the rest of the url
            # Then slices off the random number at the end off
            filename = url.split("/")
            filename = filename[len(filename)-1].rsplit('-', 1)
            filename = filename[0]
            
            # Make fullFileName for entire path and extension
            if ".jpg" in image_url:
                fullFileName = newDir+"\\"+filename+".jpg"
            elif ".jpeg" in image_url:
                fullFileName = newDir+"\\"+filename+".jpeg"
            elif ".png" in image_url:
                fullFileName = newDir+"\\"+filename+".png"
            elif ".mp4" in image_url:
                fullFileName = newDir+"\\"+filename+".mp4"
            else:
                fullFileName = newDir+"\\"+filename+".gif"

            # If file already exists in folder, don't install it
            if os.path.exists(fullFileName):
                print("File name already exists: "+filename)
                continue
            else:
                urllib.request.urlretrieve(image_url, fullFileName)
                print(filename+" acquired.")
        except:
            print("Exception occured on page: "+url)

def getPageStats(listOfPages):

    listOfDeviations = []

    for url in tqdm(listOfPages):
        page = requests.get(url)

        soup = BeautifulSoup(page.content, 'html.parser')

        time.sleep(1)

        # Grabs unlabeled favorite count from unlabeled span on page
        favorite_span = soup.find('button', style='cursor:pointer')
        favorite_span = str(favorite_span).split("<span>")
        favorite_string = (favorite_span[len(favorite_span)-1].split("</span>")[0])
        if "K" in favorite_string:
            favorite_count = int(favorite_string.replace("K", "")) * 1000
        else:
            favorite_count = int(favorite_string)
        
        # Grabs comment count from unlabeled span on page
        commentSpans = soup.find('span', {"data-hook":"comments_counter"}).find_all('span')
        comment_count = str(commentSpans[len(commentSpans)-2])
        comment_count = int(comment_count.replace("<span>","").replace("</span>",""))

        # Grabs the view count from unlabeled span on page
        view_string = str(soup.find('span', string="Views").parent).split("<span>")[1]
        view_string = view_string.split("</span>")[0]
        if "K" in view_string:
            view_count = int(view_string.replace("K", "")) * 1000
        else:
            view_count = int(view_string)

        listOfDeviations.append(Deviations(url, favorite_count, view_count, comment_count))

    return listOfDeviations