# ImageSlideShow
# Tested for version FVCOM 5.0.1 (intel) (X)
# Build: ifvcom501.org (@vsf.calc1)
# COSUrFI 2024
# Jari í Hjøllum, Knud Simonsen
# Version 1.1 31-10-2024
#
# This scripts plots data from a nc file.
# Edit:
# datapath  : The path of the input file.
# datafile    : The filename of the input file.
#
# Inspiration from : https://www.w3schools.com/howto/howto_js_slideshow.asp
#========CONSTANTS - DO NOT CHANGE==============================================
#--------VERSION----------------------------------------------------------------
VERSION         = "1.1 (31-10-2024)"
#========IMPORT=================================================================
import os
import fvcomlibio as io
import fvcomlibutil as u
import sys
import glob
#========CONSTANTS - DO NOT CHANGE==============================================
#--------VERSION----------------------------------------------------------------
VERSIONSTRING   = "ImageSlideShow v. {} by Jari í Hjøllum, 2024".format(VERSION)
THISFILESTRING  = "This file was generated at {}".format(u.generateNowTime())
#========Verbose/Debugging output===============================================
VERBOSE = True
#========CMDLINEPARAMS==========================================================
cmdparams = []
nargs = len(sys.argv)
print("Parameters ({}): ".format(nargs))
for i in range(nargs):
    print(sys.argv[i])

for i in range(nargs):
    cmdparams.append(sys.argv[i])

#========CMDLINEPARAMS==========================================================
imagepath         = "."
imagefilemask     = "*.png"
moviefile         = "san.mov"
indexfile         = "index.html"

params=u.parse_kv_pairs(cmdparams[1])
#print(list(dict.fromkeys(params)))
for y in params:
    print (y,':',params[y])
print("=======")


if ("imagepath" in params):       imagepath         = params["imagepath"]
if ("imagefilemask" in params):   imagefilemask     = params["imagefilemask"]
if ("moviefile" in params):       moviefile     = params["moviefile"]
if ("indexfile" in params):       indexfile     = params["indexfile"]

print("Image path       : {}".format(imagepath))
print("Image file mask  : {}".format(imagefilemask))
print("Movie file       : {}".format(moviefile))
print("index file       : {}".format(indexfile))

imagefilepathfulll = imagepath+"/"+imagefilemask
indexfilefull      = imagepath+"/"+indexfile

fl = glob.glob(imagefilepathfulll)
fl.sort()
for i in range(len(fl)):
    #print("{}".format(fl[i]))
    fl[i]=os.path.basename(fl[i])
    #print("{}".format(fl[i]))



str = io.getFileContent("imageslideshow_base.html")
element = "<div class=\"mySlides fade\">\n <div class=\"numbertext\">{} / {}</div>\n<img src=\"{}\" style=\"width:100%\">\n<div class=\"text\">{} / {}</div>\n</div>\n\n"
dot = "<span class=\"dot\" onclick=\"currentSlide({})\"></span>\n"

elements = "\n"
dots = "\n"

n = len(fl)
for i in range(n):
    elements = elements + element.format(i+1,n,fl[i],i+1,n)
    #print(elements)
    dots = dots + dot.format(i+1)

str = str.replace("<ELEMENTS>",elements)
str = str.replace("<DOTS>",dots)
str = str.replace("<MOVIE>","<a href=\"{}\">Animation</a>".format(moviefile))

io.writeFile(indexfilefull,str)






