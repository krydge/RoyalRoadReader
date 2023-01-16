
from urllib.request import urlopen, Request, build_opener, install_opener, urlretrieve
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import bs4
import os
import csv

def callUrl(req)-> bs4:
    try:
        return BeautifulSoup(urlopen(req).read(),'html.parser')
    except HTTPError as e:
        print(e)
    except URLError as e:
        print(e)
def printPage(page):
    print(page.getText())
def printHtml(page):
    print(page)
def stripurl(url):
    url = url.replace('https://www.','')
    urlparts = url.split('.')
    return urlparts[0]
def writeHtml(page, url):
    url = stripurl(url)
    f = open(f'{url}page.html', "w")
    f.write(str(page))
    f.close()
def getAllHrefs(links):
    if 'len(links)>0':
        for link in links:
            try:
                if 'href' in link.attrs:
                    print(link.attrs['href'])
            except Exception as e:
                print(e)

def getBookTitle(page):
    titleobj = page.findAll('h1',{'property':'name'})
    title = titleobj[0]
    return title.text

def getChapterName(chapter):
    chapter = chapter.split('/')
    return chapter[len(chapter)-1]

def getChapters(chapters, url, title):
    newchapters =[]
    if url is not None:
        for chapter in chapters:
            chapterUrl = getChapterUrl(url, chapter)
            title = getChapterName(chapter=chapter)
            req = Request(chapterUrl, headers={'User-Agent': 'Mozilla/5.0'})
            bs = callUrl(req)
            writeHtml(bs,chapterUrl )
            newchapters.append({'title':title, 'chapterContent':getChapterAsString(bs)})
        return newchapters

def getChapterAsString(chapterbs) :
    content = chapterbs.find_all("div", {"class": "chapter-content"})  
    text = content[0].text
    text = text.encode("ascii","ignore")
    text = text.decode()
    return text
    
def writeChapter(chapter, bookTitle):
    f = open(f'{bookTitle}/{chapter["title"]}.txt', "w")
    f.write(str(chapter["chapterContent"]))
    f.close()

def getChapterUrl(baseUrl, chapterUrl):
    split = baseUrl.split('/')
    newurl=''
    for x in split:
            if x == split[len(split)-2]:
                pass
            elif x == split[len(split)-1]:
                pass
            elif x == split[len(split)-3]:
                pass
            else:
                newurl = newurl+'/'+x
    return newurl.removeprefix('/')+chapterUrl

def getNumberOfChapters(chapterLinks):
    return len(chapterLinks)

def createFolder(name):
    if os.path.exists(name):
        return
    os.mkdir(name)

def getCoverLink(bookURL):
    bookLink = bookURL.find('img',{'property':'image' })
    if len(bookLink) is not None:
        bookLink = bookLink.get('src')
    print(bookLink)
    return bookLink

def downloadCover(bs, bookTitle):
    #bookTitle = bookTitle.replace(" ","")
    # Adding information about user agent
    opener=build_opener()
    opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
    install_opener(opener)

    # setting filename and image URL
    image_url = getCoverLink(bs)
    filename = f'./{bookTitle}/0-CoverImage-{bookTitle}.jpg'

    # calling urlretrieve function to get resource
    try:
        urlretrieve(image_url, filename)
    except Exception as e:
        print(e)
        print('Failed to get Cover Image')

def getNumPages(page):
    links = page.find_all('ul', {'class':'pagination justify-content-center'})
    links = links[0]
    links = links.find_all('a')
    numbers = []
    highNum = 1
    for link in links:
        try:
            number  = int(link.get('data-page'))
            if number>highNum:
                highNum=number
        except Exception as e:
            print(e)
    return highNum

def getAndUpdateBookSelection():
    url = ''
    url = "https://www.royalroad.com/fictions/complete"
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    bs = callUrl(req)
    numPages = getNumPages(bs)
    booksFilePaths = []
    books = bs.find_all('h2',{'class':'fiction-title'})
    for book in books:
            book = book.find('a')
            book = book.get('href')
            booksFilePaths.append(book)
    for page in range(2,numPages):
        url = f"https://www.royalroad.com/fictions/complete?page={page}"
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        bs = callUrl(req)
        books = bs.find_all('h2',{'class':'fiction-title'})
        for book in books:
            book = book.find('a')
            book = book.get('href')
            booksFilePaths.append(book)
    with open('./bookLinks.csv','w') as csvfile:
        bookWriter = csv.writer(csvfile)
        bookWriter.writerow(['Book URL'])
        for book in booksFilePaths:
            bookWriter.writerow([str(book)])
    return set(booksFilePaths)

def getBookSelection():
    with open('./bookLinks.csv', 'r') as BookFile:
        bookreader = csv.reader(BookFile)
        books = []
        for book in bookreader:
            books.append(book)
        nbooks = []
        for book in books:
            if book ==[]:
                pass
            else:
                book = book[0]
                nbooks.append(book)
        return nbooks

def makeBook(bookUrl):
    url = 'https://www.royalroad.com'+bookUrl
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    bs = callUrl(req)
    bookTitle=getBookTitle(bs)
    bookFolder = './'+bookTitle
    createFolder(bookFolder)
    downloadCover(bs, bookTitle=bookTitle)
    links = bs.findAll('tr')
    chapters = []
    for link in links:
        if link.get("data-url"):
            chapters.append(link.get("data-url"))
    chapterobjs =getChapters(chapters=chapters, url=url, title=bookTitle)
    for chapter in chapterobjs:
        writeChapter(chapter=chapter, bookTitle=bookTitle)
        
def main():
    try:
        print(getBookSelection())
    except HTTPError as e:
        print(e)
    except URLError as e:
        print(e)
    except Exception as e:
        print(e)


if __name__=="__main__":
    main()