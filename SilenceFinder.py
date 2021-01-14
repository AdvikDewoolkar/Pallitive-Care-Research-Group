#Import all needed tools and libraries
import re
from itertools import groupby
import os, glob
import csv
#from somtime.SelfOrganizingMap import SelfOrganizingMap
#import numpy as np

#Main Function to check all files in the folder
#and then open and run the progam on each file
def main():
    enddict = {}
    #pull all files from directory
    x = (glob.glob('./*.txt'))
    #for each file run this program
    for i in range(len(x)):
        #exception check
        try:
            #open files
            infile = open(x[i], 'r')
        except:
            print("A Failure has Occured")
        else:
            #remove the lines from the file
            #and remove the line breaks
            documentlist = []
            for line in infile:
                part = line.split("::")
                add_to_list = part[-1].replace('\n', '')
                documentlist.append(add_to_list)
            mend = ""
            for i in range(len(documentlist)):
                mend += (documentlist[i])
            #call all needed functions
            #call function to find first silence
            first = find_the_break(mend)
            #call function to find all sequencal silences
            clean = find_silence(mend)
            #send to clean all found silences and outwrite them
            printdict = organize(clean, first)
            enddict.update(printdict)
        finally:
            infile.close()
    output_txt(enddict)
    
#find the distance between the start and end "ee"
def find_the_break(mend):
    #needed lists
    mylist = []
    hold = []
    end = []
    #loop for finding starts and ends for this function
    for i in mend.split():
        if i.startswith("<ee"):
            hold.append(mend.find(i))
        if i.startswith("<\ee"):
            end.append(mend.find(i))
    #loop for using starts and ends to find the words between
    x = 0
    while x < (len(hold)):
        mylist.append(mend[(hold[x]): (end[x])])
        x += 1
    #return this to the main function
    return mylist

#function to find all sequencal silence
def find_silence(mend):
    #lists for all needed things
    start = []
    #end terms
    s1 = [m.start() for m in re.finditer('<s1>', mend)]
    s2 = [m.start() for m in re.finditer('<s2>', mend)]
    s3 = [m.start() for m in re.finditer('<s3>', mend)]
    #final set
    hold = set()
    #pull full ends silence for later
    #so that each silence can be labled correctly
    for i in range(len(s1)):
        s1[i] = s1[i] + 4
    for i in range(len(s2)):
        s2[i] = s2[i] + 4
    for i in range(len(s3)):
        s3[i] = s3[i] + 4
    #pull the starting term for each term
    for i in mend.split():
        if i.startswith("<\ee"):
            start.append(mend.find(i))
    #using the start term and needed end terms to
    #find and add the that to needed list
    x = 0
    while x < (len(start)):
        #add s1 terms
        for i in range(len(s1)):
            if len(mend[(start[x]): s1[i]]) != 0:
                hold.add(mend[(start[x]): s1[i]])
        #add s2 terms
        for i in range(len(s2)):
            if len(mend[(start[x]): s2[i]]) != 0:
                hold.add(mend[(start[x]): s2[i]])
        #add s3 terms
        for i in range(len(s3)):
            if len(mend[(start[x]): s3[i]]) != 0:
                hold.add(mend[(start[x]): s3[i]])
        x += 1
    #at this point you have isolated the lists for the distance between <ee>
    #at the distance between <ee> and <s(1,2,3)> now remove all silence types
    #for counting and log what silence it was, maybe do this above, (dic?)
    clean = clean_list(hold)
    #returned cleaned lists to the main function
    return clean

#function to remove the start term from the s(1,2,3)
#silences and then returm them to the main list
def clean_list(myset):
    #convert set to list
    hold = list(myset)
    #loop to go through list and remove that start term
    i = 0
    while i < len(hold):
        sentence = hold[i]
        result = [m.start() for m in re.finditer('<ee', sentence)]
        if len(result) != 0:
            #delete that start term
            del hold[i]
        i += 1
    #return to find_silence function
    return(hold)

#the function that removes all <> terms from the lines
#and organizes them by start term
#passes that on to the outwrite function
def organize(clean, first):
    #need lists and dicts
    starts = []
    organized = dict()
    #remove the <ee###> words from the first term
    #this is for finding true word count
    for i in range(len(first)):
        first[i] = (first[i])[1:]
        endchar = first[i].find('>')
        starts.append(first[i][0:endchar])
        organized[first[i][0:endchar]] = set()
        organized[first[i][0:endchar]].add(first[i])
    #remove all odd <> terms that arent at the end of
    #the clean lines
    for o in range(len(clean)):
        clean[o] = (clean[o])[2:]
        i = 0
        while i < len(starts):
            starters = starts[i] + '>'
            endchar = clean[o].find('>')
            z = (clean[o][0: endchar])
            organized[z].add(clean[o])
            i += 1
    #call the remover function
    printdict = remover(organized, first)
    return printdict
#the function that removes all extrenious <> terms
#add passes that on to the outwrite function
def remover(organized, first):
    #needed lists
    starts = []
    finaldict = dict()
    #takes the first line add converts it to a set
    #with needed start term to add it to the finaldict
    #dictionary
    for i in range(len(first)):
        first[i] = "e" + (first[i])[1:]
        endchar = first[i].find('>')
        starts.append(first[i][0:endchar])
        finaldict[first[i][:endchar]] = set()
    #add corrected lines from the rest of the silences
    #to the dictonary finaldict 
    for key in organized:
        mylist = list(organized[key])
        for i in range(len(mylist)):
            save = (mylist[i][-5::])
            words = (mylist[i][:-5:])
            x = (re.sub("[\<\[].*?[\>\]]", "", words))
            readd = x + save
            finaldict[key].add(readd)
    #call the output function
    printdict = output(finaldict)
    return(printdict)
#this function converts everything to the corrected
#format for out put and then prints(or outwrites) everything
def output(finaldict):
    #convert this dict to get a list
    #of just the keys
    printdict = dict.fromkeys(finaldict)
    #opens clean dictionary with keys
    #that are the same as finaldict
    for key in printdict:
        printdict[key] = []
    #addes the silences to the list
    #with just the lens of the lines
    #add what type of silence that line is
    for key in finaldict:
        #open filler lists

        keydict = {}
        finallist = list(finaldict[key])
        #loop to go through finaldict
        #add add what is needed
        for i in range(len(finallist)):
            line = finallist[i]
            char = line.find('>')
            endchar = (line.find('>')) + 2
            if line.endswith('>'):
                x = line[endchar:-4:]
                z =  x.split()
                printdict[key].append((line[-4::] + " " + str(len(z))))
            else:
                x = line[endchar:]
                z = x.split()
                printdict[key].append(str(len(z)))
    #organizes it so that <ee###> silence is first
    #in the list
    for i in printdict:
        printdict[i].sort(key = lambda item: ([int,str].index(type(item)), item))
    if len(printdict) != 0:
        for key in printdict:
            printdict[key][0] = key + " " + printdict[key][0]
    return(printdict)
def output_txt(enddict):
    try:
        filename = input("What is the name of the outfile: ")
        outfile = open(filename, 'a')
    except:
        print("An error has occured, does your name end in .txt?")
    else:
        for key in enddict:
            outfile.write(str(enddict[key])[1:-1:])
            #for i in range(len(enddict[key])):
                #outfile.write(enddict[key][i])
                #outfile.write(", ")
            outfile.write('\n')
    finally:
        outfile.close()
main()

