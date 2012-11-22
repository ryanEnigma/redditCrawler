import matplotlib.pyplot as plt
import cPickle as p
import math, os
import cairo
import cairoplot

"""
After you have finsished crawling reddit for all your information you can run this file to give you
your resulting images. Most likely you will have to comment out the cairo imports at the top along with
the donut graph function at the bottom, because that was a pain in the ass to install and very
unlikely you have the module


NOTE: You will not see any data come up on the line graph UNTIL you have 3 points of data
So until your web crawler saves three front pages to your pickle file, you will not get any
visualizaition.. You could remove the lines
if len(line[1]) < 3:
            continue

and you will get info after your first query
"""

#this is where your reddit data is stored.
redditData = p.load( open("frontPage.p"))
#this si where you would like to save your final images
saveDir = ""

#Graph ONLY the first 25 posts in the file. AKA page 1
def lnGraphTop25():
    fileSave = os.path.join(saveDir, "Top25.png")
    posts = lineGraphFrontPage()
    plt.figure()
    
    figprops = dict(figsize=(5,5), dpi=100, facecolor='white')
    fig1 = plt.figure(1,**figprops)
    
    for line in posts[:25]:
        #This gets rid of small data, posts that only appeared for 2 queries
        if len(line[1]) < 3:
            continue
        y = line[1]
        x = line[2]
        plt.plot(x,y)

    #reverse y axis so it goes 25-1
    plt.ylim(plt.ylim()[::-1])
    #text for bottom row
    plt.xlim(1, 14)
    
    fig1.canvas.draw()
    #use the line below if you want to view the image but not save, then comment the line out below it
    #plt.show()
    fig1.savefig( fileSave, dpi=300,bbox_inches='tight')
    plt.clf()#clear


#Line Graph EVERY UNIQUE post... this is ugly
def lnGraphAll( ):
    fileSave = os.path.join(saveDir, "AllPosts.png")
    posts = lineGraphFrontPage()
    plt.figure()

    figprops = dict(figsize=(5,5), dpi=100, facecolor='white')
    fig1 = plt.figure(1,**figprops)

    for line in posts:
        #This gets rid of small data, posts that only appeared for 2 queries
        if len(line[1]) < 3:
            continue
        y = line[1]
        x = line[2]
        plt.plot(x,y)

    #reverse y axis so it goes 25-1
    plt.ylim(plt.ylim()[::-1])
    #text for bottom row
    plt.xlim(1, 14)
    
    fig1.canvas.draw()
    #plt.show()
    fig1.savefig( fileSave, dpi=300,bbox_inches='tight')
    plt.clf()#clear

#this is the only function that needs cairo and cairo plot
#Takes the data from donutFronPageSub() and turns it into a donut graph
def donutGraphAll():
    saveFile = os.path.join(saveDir, "donutSubReddit.png")
    subReddDict = donutFrontPageSub()
    cairoplot.donut_plot(saveFile, subReddDict, 700, 700, background = (0,0,.2), gradient=True)



#final data looks like [postName, postPosition, Itterater(time)]
#postPosition and time is a list of lists so your final data really looks like
#["Title", [4,2,5,8], [1,2,3,4]] This gives us our X and Y data for matplib
def lineGraphFrontPage():
    time = 1#this should be a time associated with when python queried reddit!!
    
    positionList = []
    #loop over front page
    for frontPage in redditData:
        #loop over posts in page
        for post in frontPage:
            #if list is empty auto add the post
            if not positionList:
                positionList.append([post[2], [post[0]], [time]])
                continue
            #this holds wethre or not we have the data in the list
            notStored = False
            #loop over all stored names to see if current post is in it
            for item in positionList:
                #if the current post is not contained in the data list append it
                if post[2] not in item:
                    notStored = True
                #we found the name inside the data list
                else:
                    #store the current rank
                    item[1].append(post[0])
                    item[2].append(time)
            
            if notStored:
                #add the post name
                positionList.append([post[2], [post[0]], [time]])

        #loop to next time queired
        time += 1
    return positionList


#oh jeez these are ugly!
#a quick overview of what you will see in this def
#loop over all the posts and based onthe title(post[2]) i determine
#the uniqueness of the post. If the post is unique I append it to the
#array uniquePost[] along with the subreddit(post[4])
def donutFrontPageSub():
    #end the end this will hold the subreddit and a # for how many times appeared
    subRedditDict = {}
    #This holds the title, and the subreddit
    uniquePosts = []
    
    #first find all the Unique posts in our data
    for frontPage in redditData:
        #loop over posts in page
        for post in frontPage:
            #this places the first item in the list(since it is unique)
            if not uniquePosts:
                #hold Post name and Subreddit
                uniquePosts.append([ post[2], post[4] ])
                continue
            #keep track if the post is in the list
            notStored = False
            #loop over all stored names to see if current post is in it
            for item in uniquePosts:
                #if the current post is not contained in the data list append it
                if post[2] not in item[0]:
                    notStored = True
            
            #the post is unique, append it
            if notStored:
                #add the post name and subreddit
                uniquePosts.append([ post[2], post[4] ])
    
    """turning the lists in to a dictionary"""
    #Now turn the lists in to a dictionary containing the subreddit and a counter for times found
    for post in uniquePosts:
        #the sub redd is not in the Dict so add it and make the counter 1
        if post[1] not in subRedditDict:
            subRedditDict[post[1]] = 1
        #The subreddit already exists in our dictionary so append 1 to it
        else:
            subRedditDict[post[1]] = subRedditDict[post[1]] + 1
    return subRedditDict


lnGraphAll()
lnGraphTop25()
donutGraphAll()
