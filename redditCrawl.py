#reddit front page crawler
import urllib as url
import cPickle as pickle
import os
import time

"""
The best way to run this file is by calling redditWatch() this will auto query reddit
every 20 minutes and save both top 25 posts and the top post if unique. Other wise if
you want to run this file by hand you have to do:

#save reddit front page to HDD
webCrawl()
#simple proc to turn lines in to one long line
info = openReddit()
#first pass at seperating data
posts = seperatePosts( info )
#last pass at seperating useful data to lists
processed = processPosts( posts )
#pickle file save list of top 25 posts
trackTop25( processed )#save all 25 top links
#pickle file save of only top Unique* post
saveTopPost( processed )#save only top post if diff


Be sure to set your save directory down there vvvv
"""

#Add a DIRECTORY path where you want to save your final text files
saveDir = ""

#query reddit and save the file to drive
def webCrawl():
    #save file loc
    webCrawlFile = os.path.join( saveDir, "FrontPage.txt")
    #website to query
    website = url.urlopen('http://www.reddit.com/r/all/')
    #read the webdata
    fileSave = website.read()
    
    #save to disk, after making sure file exists
    if not os.path.exists(webCrawlFile):
        x = file(webCrawlFile, "w")
        x.close()
    mkFile = open( webCrawlFile, "w+")
    #save
    mkFile.write(fileSave)
    mkFile.close()


#this reads in the file and essentialy turns each line in to one long string.
def openReddit():
    webCrawlFile = os.path.join( saveDir, "FrontPage.txt")
    redditPage = open(webCrawlFile)

    redditLine=''
    for line in redditPage:
        #make one lonnngg string
        redditLine += line
    
    return redditLine


#Starts cutting down the data.
#This will seperate all the data needed for each post in to a seperate list item
#The data is still a long string and is very messy, it goes on to processPosts() next
def seperatePosts( redditLine ):
    #split the front page in to each post
    posts=[]
    while 1:
    #Start of post is '<span class="rank"'
        postStart = redditLine.find('<span class="rank"')
        if postStart != -1:
            #end of post is the '</a>' after 'class="subreddit hover"'
            #find the almost end, this is a unique phrase round at almost end of line
            almostEnd = redditLine[postStart:].find('class="subreddit hover"')
            #now find the last part of the post
            postEnd = redditLine[almostEnd:].find('class="comments"')
            #now add almostend to postend to get actual position
            postEnd += almostEnd
            #we now have the start and end point of the reddit post, append to list
            posts.append(redditLine[postStart:postEnd])
            #remove post from redditLine
            redditLine=redditLine[postEnd:]
        else:
            break
    return posts


#after getting the ugly info back from reddit we sort though it here
#The output will be [rank, karma, title, date, subRedd], date is UTC!!
#this processed info is then passed to our pickler, where we save out
#both the top post to one file, and the top 25 to another
def processPosts( posts ):
    #split post in to its smaller parts
    top25=[]
    for post in posts:
        #Rank
        rankFind  = post.find('class="rank"')
        rankStart = post[rankFind:].find(">") + 1#add 1 for str len
        rankEnd   = post[rankFind:].find("<")
        rankStart += rankFind
        rankEnd   += rankFind
        rank = post[rankStart:rankEnd]
        #Skip if no rank was found
        if not rank:
            continue
        
        
        #Karma
        karmaStart = post.find('score unvoted">') + 15#add 15 for str len
        karmaEnd   = post[karmaStart:].find("<")
        karmaEnd += karmaStart
        karma = post[karmaStart:karmaEnd]
        
        #i think these are ad's
        if "&bull" in karma:
            continue


        #Title
        titleNotStart = post.find('<a class="title "') + 17
        titleStart = post[titleNotStart:].find(">") + 1 + titleNotStart
        titleEnd = post[titleStart:].find("</a>") + titleStart
        title = post[titleStart:titleEnd]


        #Time subm
        dateStart = post.find('time title="') + 12#add 12 for str len
        dateEnd   = post[dateStart:].find('UTC"')
        dateEnd += dateStart
        date = post[dateStart:dateEnd]
        
        #i think these are ad's
        if not date:
            continue

        
        #Sub Redd
        subStart = post.find('subreddit hover" >') + 18#add 18 for str len
        subEnd   = post[subStart:].find('</a>')
        subEnd += subStart
        subRedd = post[subStart:subEnd]

        #i think these are ad's
        if not subRedd:
            continue

        #add the info to array
        top25.append([rank, karma, title, date, subRedd])
    return top25


#this saves only rank 1 of a post to a pickle file this
#will show what time is the best to post and hit rank 1
#Only a unique top post will be added. There will be no duplicates in the pickeld file
def saveTopPost( processed ):
    #path to saved file
    rankOneFile = os.path.join(saveDir, 'rank_one_Data.p')
    #you can only load a pickle file if it exists and has data
    if os.path.exists(rankOneFile):
        #open file.
        savedRanks = pickle.load( open(rankOneFile, "rb") )
    #otherwise make a temp list
    else:
        savedRanks = []

    #this next chunk checks if the array already contains the top post we just quiered from reddit
    add = True#a boolean, if true then we add the current top to the file
    #loop over our list in the file
    for rank in savedRanks:
        #is the saved title(rank[2], the same as the current post title 
        if rank[2] == processed[0][2]:
            #weve already added this post to our file, do not add again
            add = False
    #if add is still true then add the current post to the file
    if add:
        print "Rank 1 is new, file saving"
        savedRanks.append(processed[0])

    #save back to file
    pickle.dump( savedRanks, open(rankOneFile, "wb") )
    #close


#this will show the life of a post as it rises and falls on the front page
#all 25 top posts in r/all are saved out. 
def trackTop25( processed ):
    #path to save file for top 25
    top25File = os.path.join(saveDir, "FrontPage.p")
    
    #you can only load a pickle file if it exists and has data
    if os.path.exists(top25File):
        #open the file
        savedFront = pickle.load( open(top25File, "rb") )
    #if file doesnt exist make a temp list
    else:
        savedFront = []
    print "saving top 25 posts on reddit /all"
    #append the current top 25 to the existing list
    savedFront.append( processed )

    #save the new list out to file
    pickle.dump( savedFront, open(top25File, "wb") )


#crawl the webpage and save process the data
#then pickle the data out to our two files
def redditWatch():
    while 1:
        webCrawl()
        info = openReddit()
        posts = seperatePosts( info )
        
        #make sure reddit did not block us
        if not len( posts ):
            print "Reddit didn't let you query..."
            #sleep another minute
            time.sleep(60)
        
        #if the array is populated
        if len(posts):
            processed = processPosts( posts )
            trackTop25( processed )#save all 25 top links
            saveTopPost( processed )#save only top post if diff
        
        time.sleep(1200)




redditWatch()
