#!/bin/python
import sys, os
import re
import urllib.request




class key_values:
    def __init__(self,citekey,values):
        self.citekey = citekey
        self.values = values


def get_data(datastring):
    attributevalue = []
    start = 0
    stop = datastring.find("@")
    if stop > 0:
        datastring=datastring[start:stop]
    else:
        datastring = datastring[start:]
    stop = datastring.rfind("}")
    datastring=datastring[start:stop] #key,att1={txt1},att2={txt2}.... last , can be present or not
    start = datastring.find("{")
    stop = datastring.find(",")
    citekey = datastring[start+1:stop]
    #from now starts attribute extrations
    cont = True #we suppose to have almost one attribute
    while cont:
        datastring = datastring[stop+1:]
        start = 0
        stop = datastring.find("}")
        analyzedstring = datastring[start:stop]
        analyzedstring = analyzedstring.strip();
        stop = analyzedstring.find("=")
        key = analyzedstring[start:stop]
        key = key.strip()
        start = analyzedstring.find("{")
        value = analyzedstring[start+1:]
        value = value.strip()
        attributevalue.append(key)
        attributevalue.append(value)
        stop = datastring.find(",")
        if stop == -1:
            cont = False
        else:
            stop = datastring.find("}")
            datastring = datastring[stop + 1:]
            stop = datastring.find(",")
    #print(len(attributevalue))
    returnvalue = key_values(citekey, attributevalue)
    return returnvalue


bibfile = sys.argv[1]
f = open(bibfile, "r")
recordstring = f.read()
classes = list(dict.fromkeys(re.findall('@(.*){', recordstring)))
recordstring=recordstring.replace('\n',' ')
#clean from {\
recordstringcopy=recordstring
recordstring=""
idx = 0
graphdepth = 0
while idx <= len(recordstringcopy)-2:
    simplycopy = True
    if (recordstringcopy[idx] == "{"):
        graphdepth = graphdepth+1
    if (recordstringcopy[idx] == "}"):
        graphdepth = graphdepth-1

    skipcopy = False
    if ( ( (recordstringcopy[idx] == "{") & (graphdepth >= 3) ) or
        ( (recordstringcopy[idx] == "}") & (graphdepth >= 2) ) ):
            skipcopy = True
            if recordstringcopy[idx] == "{":
                recordstring = recordstring + "__open_graph__"
            if recordstringcopy[idx] == "}":
                recordstring=recordstring+"__close_graph__"
    if ((recordstringcopy[idx] == "@") & (graphdepth >= 1)):
        skipcopy = True
        recordstring = recordstring + "__at__"
    if skipcopy == False:
        recordstring=recordstring+recordstringcopy[idx]
    idx = idx+1

# recordarray=recordstring.split"
for classelementname in classes:
    fileToWrite = classelementname+".tex"
    stringToWrite = ""
    # To generate, if present
    # Title
    # Author(s)
    # per Journal: journal + publisher
    # DOI
    # abstract
    # citeref

    attributestoprint = ["title", "author", "doi", "abstract"]
    if classelementname == "article":
        attributestoprint = ["title", "author", "journal", "publisher", "doi", "abstract"]

    elementnametosearch = "@" + classelementname + "{"
    classelementstarts = [i for i in range(len(recordstring)) if recordstring.startswith(elementnametosearch, i)]
    for classelementstart in classelementstarts:
        #print(classelementname +" "+str(classelementstart))
        substringstartswithelement = recordstring[classelementstart+1:]
        stoptoken=substringstartswithelement.find("@")
        if stoptoken > 1:
            substringstartswithelement = substringstartswithelement[:stoptoken]
        keyvalue=get_data(substringstartswithelement)

        #print("key "+keyvalue.key)
        for idxatt in attributestoprint:
            for idx in range(int(len(keyvalue.values)/2)):
                #print(idx)
                if (keyvalue.values[2*idx] == idxatt):
                    # reinsert graph
                    txt = keyvalue.values[2 * idx + 1]
                    txt = txt.replace("__open_graph__", "{")
                    txt = txt.replace("__close_graph__", "}")
                    txt = txt.replace("__at__", "@")
                    txt = txt.replace("_", "\\_")
                    txt = txt.replace("&", "\\&")
                    attributetitletoprint = idxatt.capitalize()
                    if attributetitletoprint == "Doi":
                        attributetitletoprint = "DOI"
                    if attributetitletoprint == "Author":
                        if txt.find("and")>1:
                            attributetitletoprint = "Authors"
                        if txt.find(",")>1:
                            attributetitletoprint = "Authors"
                    stringprint = False
                    if idxatt == "title":
                        stringprint = True
                        httppage = "https://openportal.isti.cnr.it/results?qv=\"" + txt + "\""
                        stringToWrite = stringToWrite+"\\textbf{"+attributetitletoprint+"}: \href{" + \
                                        httppage + "}{" + txt + "}\\\\ \n"
                        #print(httppage)
                        #contents = urllib.request.urlopen("\""+httppage+"\"").read()
                        #contents = urllib.request.urlopen("https://openportal.isti.cnr.it/results?qv=Venturino").read()
                    if idxatt == "doi":
                        stringprint = True
                        stringToWrite = stringToWrite+"\\textbf{"+attributetitletoprint+"}: \doix{"+ txt +"}\\\\ \n"
                    if idxatt == "abstract":
                        stringprint = True
                        stringToWrite = stringToWrite+"\\textbf{"+attributetitletoprint+"}: \\textit{"+ txt +"}\\\\ \n"
                    if  stringprint == False:
                        stringToWrite = stringToWrite + "\\textbf{" + attributetitletoprint + "}: " + txt + "\\\\ \n"
        #add cite key
        stringToWrite = stringToWrite + "\cite{"+keyvalue.citekey+"}\\\\ \\vspace{5mm} \\\\ \n"
    with open(fileToWrite, 'w') as f:
        f.write(stringToWrite)

