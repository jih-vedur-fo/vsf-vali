# fvcomgrid.py - FVCOMGrid for for FVCOM
# Tested for version FVCOM 5.0.1 (intel)
# Build: ifvcom501.wd.lag (@fvcom-u18-skeid)
# COSUrFI 2024
# Jari í Hjøllum, Knud Simonsen
# Version 1.6 05-06-2024
import os
import numpy as np
import sys
import fvcomlibio as io
import fvcomlibutil as u
import math
import re

VERBOSE = False
CUTOFORPHANCOUNT = 99999999
iNodeFieldCount = 5
inX = 0
inY = 1
inZ = 2
inDep = 3
inCor = 4
iCellFieldCount = 3
ic1 = 0 # index of node 1
ic2 = 1 # index of node 2
ic3 = 2 # index of node 3
iCellCenterFieldCount = 2 # X and Y corresponding to xc and yc in NetCDf.
icc1 = inX # x-component of center of mass
icc2 = inY # y-component of center of mass

iOrphanDictFieldCount = 2
iSpongeFieldCount = 3
isNode = 0 # int
isRadius = 1 #
isExp = 2
sSpongeExport = "{:>6d} {: .7f} {: .7f}\n"
iObcFieldCount = 3
ioIndex = 0
ioNode = 1
ioOpen = 2  # Open??
iTideFieldCount = 1
itObcNodes = 0
itcObcNodes = 2 # Obc_nodes location in cdl file
iRiverFieldCount = 6
irNode = 3

# # From : https://stackoverflow.com/questions/7632963/numpy-find-first-index-of-value-fast
# @njit
# def findfirst(item, vec):
#     # """return the index of the first occurence of item in vec"""
#     for i in range(len(vec)):
#         if (item == vec[i]).any():
#             return i
#     return -1

def norm2(a1, a2, b1, b2):
    return (math.sqrt((a1-a2)**2 + (b1-b2)**2))

class FVCOMGrid:

    def __init__(self):

        self.nodecount = -1 # Number of (valid) elements in nodes
        self.corcount = 1 # Number of (valid) elements in nodes.cor
        self.depcount = -1 # Number of (valid) elements in nodes.dep
        self.cellcount = -1 # Number of (valid) elements in cells
        self.obccount = -1  # Number of obcs
        self.orphancount = -1 # Number of orphans found/loaded
        self.orphandictcount = -1 # Number of (valid) elements in the orphandict
        self.rivercount = -1
        self.spongecount = -1 # Number of sponge fields
        self.tidecount = -1  # Number of sponge fields

        self.orphans = "" # Text list of orphans
        self.tidecdlfilecontent = []

        self.setNodesLength(self.nodecount)
        self.setCellsLength(self.cellcount)
        self.setObcsLength(self.obccount)
        self.setOrphanDictLength(self.orphandictcount)
        self.setRiversLength(self.spongecount)
        self.setSpongesLength(self.spongecount)
        self.setTidesLength(self.tidecount)


        self.nodes = []
        self.cells = []
        self.cellCenters = []
        self.obcs = np.zeros((0, iObcFieldCount),dtype=int)
        #self.cors = np.zeros((0, iCorFieldCount),dtype=float)
        #self.deps = np.zeros((0, iDepFieldCount),dtype=float)
        #self.tides = np.zeros((cnt, iTideFieldCount),dtype=object)

        self.setNodesLength(0)
        self.setCellsLength(0)

        self.enMap = [] # Map of best fitting element to each node. Use calcEleNodeMap() to build
    # def END
    #
    #===========================================================================================

    def calcEleNodeMap(self):
        self.enMap = [-1] * self.nodecount # Allocate array of length nodecount
        for i in range(self.nodecount):
            jFound = -1
            rDist = 1e12
            jindex = np.where(self.cells == i) # A quick, but clumsy way to find if
            jFound = jindex[0]-1 # -1: 0-index

            #for j in range(self.cellcount):
                #if (self.cells[j,0]==i): jFound = j
                #if (self.cells[j,1]==i): jFound = j
                #if (self.cells[j,2]==i): jFound = j
                #if (i<10 and jFound==j):
                        #print("Found for i={:6d}: j={:6d}".format(i,j))
            if (i % 1000 == 0): print(i)

                # if END
            # for j END
            self.enMap[i]=jFound
        # for i END





    # ==========================================================================================
    #
    #
    def checkOrphanNodes(self):
        self.setOrphanDictLength(self.nodecount)
        pivot = 0  # Next Valid index.
        orphans = []
        for i in range(self.nodecount):
            nodeno = i + 1  # The nodes are numbered from 1, not 0.
            nodefound = False

            itemindex = np.where(self.cells == nodeno) # A quick, but clumsy way to find if there is an occurance in the list
            nodefound = (len(itemindex[0]) > 0)

            if (nodefound):
                pivot += 1  # Update the new next valid node no
                self.orphandict[i, 0] = nodeno  # Current node index
                self.orphandict[i, 1] = pivot  # New node index. -1 indicates current was not found. not found
                # sys.stdout.write('.'+str(nodeno))
                sys.stdout.write('.')
            else:
                self.orphandict[i, 0] = nodeno  # Current node index
                self.orphandict[i, 1] = -1  # New node index. -1 indicates current was not found. not found
                sys.stdout.write('0')
                orphans.append(str(nodeno))
                # print("Orphan node found: {}".format(nodeno))
            if (i % 1000 == 0): sys.stdout.write(" " + str(round(100 * i / self.nodecount)) + "% \n")
            if (i % 200 == 0): sys.stdout.flush()

            if (i == CUTOFORPHANCOUNT):
                self.orphandictcount = CUTOFORPHANCOUNT
                break
        # for i ...
        self.orphans = "\n".join(orphans)
        self.countOrphans()
        print("Number of orphans: {}".format(self.orphancount))
        # def checkOrphans ... END

    # ==========================================================================================
    #
    #
    def countOrphans(self):
        c = 0
        for i in range(self.orphandictcount):
            if (self.orphandict[i, 1] == -1): c += 1
        self.orphancount = c;
        return self.orphancount

    # ==========================================================================================
    #
    #
    def loadCorFile(self, fn):
        print("Opening cor file: \"{}\":".format(fn))
        file1 = open(fn, 'r')
        lines = file1.readlines()
        N = len(lines)
        d = [""] * N  # List of empty string
        print("Lines in file: {}".format(N))
        # Loads the lines into list
        count = 0
        for line in lines:
            count += 1
            #             if (count<=10):
            #                print("Line {:5}: {}".format(count, line.strip()))
            d[count - 1] = line
        print("Number of lines read: {}".format(count))
        #
        # Loading the data into array
        # Read node / cell (line 1)
        s = d[0]
        ss = s.split("=")
        corcount = int(ss[1])
        #
        # Read node % cell count
        print("Cor count in file: {}".format(corcount))
        self.setCorsLength(corcount)

        #
        # Load the data into array
        offset = 1
        for i in range(offset, corcount + offset):
            j = i - offset
            #             if (j<6):
            #                 print("Reading line: {}...".format(i))
            #                 print("L{}        : [{}].".format(i,d[i])  )
            ss = d[i].split()
            f0 = float(ss[0]) #  First field
            f1 = float(ss[1]) # Second field
            f2 = float(ss[2]) # Third field
            n2=norm2(f0,self.nodes[j,inX],f1,self.nodes[j,inY])
            if (n2>1e-1):
                print("ERROR: large deviation: {}".format(n2))
                exit
            #self.nodes[j, 0] = f0
            #self.nodes[j, 1] = f1
            self.nodes[j, inCor] = f2
            # self.cells[j,3]=int(ss[4])

    #             if (VERBOSE and j<6):
    #                 print("Cells read ({}->{}) : {}  {}  {}".format(i,j,self.nodes[j][0],self.nodes[j][1],self.nodes[j][2]))
    # end def
#
    # ==========================================================================================
    #
    #
    def loadDepFile(self, fn):
        print("Opening dep file: \"{}\":".format(fn))
        file1 = open(fn, 'r')
        lines = file1.readlines()
        N = len(lines)
        d = [""] * N  # List of empty string
        print("Lines in file: {}".format(N))
        # Loads the lines into list
        count = 0
        for line in lines:
            count += 1
            #             if (count<=10):
            #                print("Line {:5}: {}".format(count, line.strip()))
            d[count - 1] = line
        print("Number of lines read: {}".format(count))
        #
        # Loading the data into array
        # Read node / cell (line 1)
        s = d[0]
        ss = s.split("=")
        depcount = int(ss[1])
        #
        # Read node % cell count
        print("Dep count in file: {}".format(depcount))
        self.setDepsLength(depcount)

        #
        # Load the data into array
        offset = 1
        for i in range(offset, depcount + offset):
            j = i - offset
            #             if (j<6):
            #                 print("Reading line: {}...".format(i))
            #                 print("L{}        : [{}].".format(i,d[i])  )
            ss = d[i].split()
            f0 = float(ss[0]) #  First field
            f1 = float(ss[1]) # Second field
            f2 = float(ss[2]) # Third field
            n2=norm2(f0,self.nodes[j,inX],f1,self.nodes[j,inY])
            if (n2>1e-1):
                print("ERROR: large deviation: {}".format(n2))
                exit
            #self.nodes[j, 0] = f0
            #self.nodes[j, 1] = f1
            self.nodes[j, inDep] = f2
            # self.cells[j,3]=int(ss[4])

    #             if (VERBOSE and j<6):
    #                 print("Cells read ({}->{}) : {}  {}  {}".format(i,j,self.nodes[j][0],self.nodes[j][1],self.nodes[j][2]))
    # end def
#
    # ==========================================================================================
    #
    #
    def loadGridFile(self, fn):
        print("Opening grid file: \"{}\":".format(fn))
        file1 = open(fn, 'r')
        lines = file1.readlines()
        N = len(lines)
        d = [""] * N  # List of empty string
        print("Lines in file: {}".format(N))
        # Loads the lines into list
        count = 0
        for line in lines:
            count += 1
            #             if (count<=10):
            #                print("Line {:5}: {}".format(count, line.strip()))
            d[count - 1] = line
        print("Number of lines read: {}".format(count))
        #
        # Loading the data into array
        nodecount = 0
        cellcount = 0
        # Read node / cell (line 1)
        s = d[0]
        if ("Node Number" in s):
            ss = s.split("=")
            nodecount = int(ss[1])
        else:
            ss = s.split("=")
            cellcount = int(ss[1])
        # Read node / cell (line 2)
        s = d[1]
        if ("Node Number" in s):
            ss = s.split("=")
            nodecount = int(ss[1])
        else:
            ss = s.split("=")
            cellcount = int(ss[1])
        #
        # Read node % cell count
        print("Node count in file: {}".format(nodecount))
        print("Cell count in file: {}".format(cellcount))
        self.setNodesLength(nodecount)
        self.setCellsLength(cellcount)
        #
        # Load the data into array
        # Load Cells first
        offset = 2
        for i in range(offset, cellcount + offset):
            j = i - offset;
            ss = d[i].split()
            self.cells[j, ic1] = int(ss[1])
            self.cells[j, ic2] = int(ss[2])
            self.cells[j, ic3] = int(ss[3])
        # for END
        #
        # Load Nodes next
        offset = cellcount + 2
        for i in range(offset, offset + nodecount):
            j = i - offset
            #             if (j<6):
            #                  print("Reading line: {}...".format(i))
            #                  print("L{}        : [{}].".format(i,d[i][:-1])  )
            ss = d[i].split()
            self.nodes[j, inX] = float(ss[1])
            self.nodes[j, inY] = float(ss[2])
            self.nodes[j, inZ] = float(ss[3])
        #             if (VERBOSE and j<6):
        #                 print("Nodes read ({}->{}) : {}  {}  {}".format(i,j,self.nodes[j][0],self.nodes[j][1],self.nodes[j][2]))
        # for END
        #
        # =======================================================================================0
        # Calculate Cell centers
        for i in range(self.cellcount):
            #
            # Calc XC
            self.cellCenters[i,inX]= ( self.nodes[self.cells[i,ic1]-1,inX] + self.nodes[self.cells[i,ic2]-1,inX] + self.nodes[self.cells[i,ic3]-1,inX]) / 3.0
            # Calc YC
            self.cellCenters[i,inY]= ( self.nodes[self.cells[i,ic1]-1,inY] + self.nodes[self.cells[i,ic2]-1,inY] + self.nodes[self.cells[i,ic3]-1,inY]) / 3.0
            # Calc YC - NOT VALID AS DEPTH is contained in the DEP file.
            #self.cellCenters[i,inZ]= ( self.nodes[self.cells[i,ic1]-1,inZ] + self.nodes[self.cells[i,ic2]-1,inZ] + self.nodes[self.cells[i,ic3]-1,inZ]) / 3.0

            if (VERBOSE):
                print("N1 N2 N3 X1 X2 X3 : {:5d} {:5d} {:5d}    {:8.1f}  {:8.1f}  {:8.1f} => {:8.1f}"
                        .format(self.cells[i,ic1], self.cells[i,ic2], self.cells[i,ic3],
                                self.nodes[self.cells[i,ic1]-1,inX], self.nodes[self.cells[i,ic2]-1,inX], self.nodes[self.cells[i,ic3]-1,inX], self.cellCenters[i,inX]))
                print("N1 N2 N3 Y1 Y2 Y3 : {:5d} {:5d} {:5d}    {:8.1f}  {:8.1f}  {:8.1f} => {:8.1f}"
                        .format(self.cells[i,ic1], self.cells[i,ic2], self.cells[i,ic3],
                                self.nodes[self.cells[i,ic1]-1,inY], self.nodes[self.cells[i,ic2]-1,inY], self.nodes[self.cells[i,ic3]-1,inY], self.cellCenters[i,inY]))

            #print("XC YC {}  {}".format(self.cellCenters[i,icc1],self.cellCenters[i,icc2]))
            #self.cellCenters[i,icc1]=self.cells[i,ic1]
        # for END
        print("Loaded grd file.")

        # end
    # ==========================================================================================
    #
    #
    def loadObcFile(self, fn):
        print("Opening obc file: \"{}\":".format(fn))
        file1 = open(fn, 'r')
        lines = file1.readlines()
        N = len(lines)
        d = [""] * N  # List of empty string
        print("Lines in file: {}".format(N))
        # Loads the lines into list
        count = 0
        for line in lines:
            count += 1
            d[count - 1] = line
        print("Number of lines read: {}".format(count))
        #
        # Loading the data into array
        # Read node / cell (line 1)
        s = d[0]
        ss = s.split("=")
        obccount = int(ss[1])
        #
        # Read node % cell count
        print("obc count in file: {}".format(obccount))
        self.setObcsLength(obccount)

        #
        # Load the data into array
        offset = 1
        for i in range(offset, obccount + offset):
            j = i - offset
            #             if (j<6):
            #                 print("Reading line: {}...".format(i))
            #                 print("L{}        : [{}].".format(i,d[i])  )
            ss = d[i].split()
            self.obcs[j, ioIndex] = int(ss[0]) #  First field
            self.obcs[j, ioNode] = float(ss[1]) # Second field
            self.obcs[j, ioOpen] = float(ss[2]) # Third field
    # end def loadObsFile


    # ==========================================================================================
    # loadRiverNmlFile
    #
    def loadRiverNmlFile(self, fn):
        print("Opening river (.nml) file: \"{}\":".format(fn))
        file1 = open(fn, 'r')
        lines = file1.readlines()
        N = len(lines)
        d = [""] * N  # List of empty string
        print("Lines in file: {}".format(N))
        # Loads the lines into list
        count = 0
        for line in lines:
            count += 1
            d[count - 1] = line
        print("Number of lines read: {}".format(count))

        rivercount = int(count / 6)
        print("River count in file: {}".format(rivercount))
        self.setRiversLength(rivercount)
        for i in range(rivercount):
            self.rivers[i, 0] = d[6 * i + 0].strip()
            self.rivers[i, 1] = d[6 * i + 1].strip()
            self.rivers[i, 2] = d[6 * i + 2].strip()
            ss = d[6 * i + 3].strip()
            self.rivers[i, 3] =int(ss.split("=")[1])
            self.rivers[i, 4] = d[6 * i + 4].strip()
            self.rivers[i, 5] = d[6 * i + 5].strip()



    # END def loadRiverNmlTideCdlFile


    # ==========================================================================================
    # loadSpgFile
    #
    def loadSpgFile(self, fn):
        print("Opening spg file: \"{}\":".format(fn))
        file1 = open(fn, 'r')
        lines = file1.readlines()
        N = len(lines)
        d = [""] * N  # List of empty string
        print("Lines in file: {}".format(N))
        # Loads the lines into list
        count = 0
        for line in lines:
            count += 1
            d[count - 1] = line
        print("Number of lines read: {}".format(count))
        #
        # Loading the data into array
        # Read node / cell (line 1)
        s = d[0]
        ss = s.split("=")
        spgcount = int(ss[1])
        #
        # Read node % cell count
        print("Spg count in file: {}".format(spgcount))
        self.setSpongesLength(spgcount)
        #
        # Load the data into array
        offset = 1
        for i in range(offset, spgcount + offset):
            j = i - offset
            ss = d[i].split()
            self.sponges[j, isNode] = int(ss[0]) #  First field
            self.sponges[j, isRadius] = float(ss[1]) # Second field
            self.sponges[j, isExp] = float(ss[2]) # Third field
    # end def loadSpgFile

    # ==========================================================================================
    # loadTideCdlFile
    #
    def loadTideCdlFile(self, fn):
        print("Opening tide (.cdl) file: \"{}\":".format(fn))
        s = io.getFileContent(fn)
        t = [] # Strings list
        tag = []
        tag.append("data:")
        tag.append("obc_nodes =")
        tag.append(";")
        t.append(s)
        for n in range(len(tag)):
            ltag = len(tag[n])
            ss = t[n]
            i = ss.index(tag[n])
            j = i+ltag
            t[n]=ss[:j]
            t.append(ss[j:])

        # Reading the tide node numbers into the structure
        t[2]=t[2].replace(";"," ")
        d = t[2].strip().split(",")
        for i in range(len(d)):
            d[i] = int(d[i].strip())
        # for i in range(10):
        #     print("Tide node {} : {:d} ".format(i+1,d[i]))
        self.tidecdlfilecontent = t
        self.setTidesLength(len(d))
        for i in range(len(d)):
            self.tides[i,itObcNodes] = d[i]

    # END def loadTideCdlFile

    #
    #
    #
    #
    #
    def readOrphanDictionary(self, fn):
        print("Opening orphan dictionary file: \"{}\":".format(fn))
        # Using readlines()
        file1 = open(fn, 'r')
        lines = file1.readlines()
        N = len(lines)
        d = [""] * N  # List of empty string
        print("Lines in file: {}".format(N))
        # Loads the lines into list
        count = 0
        for line in lines:
            line = line.strip()
            if (len(line) > 0):
                count += 1
                d[count - 1] = line
            # if ... END
        # for ... END
        #
        # Loading the data into array

        if (self.orphandictcount != count):
            self.setOrphanDictLength(count)
        orphans = []
        for i in range(count):
            ss = d[i].split()
            self.orphandict[i, 0] = int(ss[0])
            self.orphandict[i, 1] = int(ss[1])
            if (self.orphandict[i, 1] == -1): orphans.append(str(self.orphandict[i, 0] + 1))
            # if (i<25): print("L{}  {}  ->  {}".format(i,self.orphandict[i,0], self.orphandict[i,1]))
            # for ... END
        self.orphandictcount = count
        self.orphans = "\n".join(orphans)
        self.countOrphans()
        print("Number of orphans: {}".format(self.orphancount))
        # def readOrphanDictionary END

    #
    #
    #
    def reindexCells(self):
        print("Re-indexing cells....")
        for i in range(self.cellcount):
            if (self.cells[i, 0] != self.orphandict[self.cells[i, 0] - 1, 0]):
                print("ERROR ERROR {} <-> {}".format(self.cells[i, 0], self.orphandict[self.cells[i, 0] - 1, 0]))
            # if (i<25): print("Cell {}: {}  {}  {}".format(i+1,self.cells[i,0],self.cells[i,1],self.cells[i,2]))
            self.cells[i, 0] = self.orphandict[self.cells[i, 0] - 1, 1]
            self.cells[i, 1] = self.orphandict[self.cells[i, 1] - 1, 1]
            self.cells[i, 2] = self.orphandict[self.cells[i, 2] - 1, 1]
        print("Re-indexing cells.... DONE")

    # def reindexOrphans END
    #
    #
    #

    #
    #
    def reindexNodes(self):
        print("Re-indexing nodes....")
        if (True or self.nodecount == self.orphandictcount):
            for i in range(self.orphandictcount):
                if (self.orphandict[i, 1] != -1):
                    # print("Index change {} -> {}  ".format(self.orphandict[i,0],self.orphandict[i,1]))
                    # print("1 Node {} before : {} {} {}".format(self.orphandict[i,1],self.nodes[self.orphandict[i,1]-1,0], self.nodes[self.orphandict[i,1]-1,1], self.nodes[self.orphandict[i,1]-1,2]))
                    # print("2 Node {} before: {} {} {}".format(self.orphandict[i,0],self.nodes[self.orphandict[i,0]-1,0], self.nodes[self.orphandict[i,0]-1,1], self.nodes[self.orphandict[i,0]-1,2]))
                    self.nodes[self.orphandict[i, 1] - 1] = self.nodes[self.orphandict[i, 0] - 1]
                    # print("3 Node {} after : {} {} {}".format(self.orphandict[i,1],self.nodes[self.orphandict[i,1]-1,0], self.nodes[self.orphandict[i,1]-1,1], self.nodes[self.orphandict[i,1]-1,2]))
                #                 else:
                #                     if (i<25):
                #                         print("Node {} is orphan.".format(i+1))
                # if (i % 1000 == 0):
                #     sys.stdout.write('\033[2K\033[1G')
                #     sys.stdout.write(str(round(100 * i / self.nodecount)) + "% ")
                #     sys.stdout.flush()
        else:
            print(
                "ERROR:: Number of nodes and number of elements in the orphan dictionary do not match. Have you already run the re-indexing routine? Or have you not yet populated the dictionary, either from file or through generation?")
        # if/else ... END
        print("Old node count: {}. New node count: {}.".format(self.nodecount,
                                                               self.orphandict[self.orphandictcount - 1, 1]))
        self.nodecount = self.orphandict[self.orphandictcount - 1, 1]
        if (self.corcount>-1): self.corcount = self.nodecount
        if (self.depcount > -1): self.depcount = self.nodecount
        print("Re-indexing nodes.... DONE")
    # def reindexNodes ... END

    #
    #
    def reindexObcs(self):
        print("Re-indexing obcs....")
        for i in range(self.obccount):
            if (self.obcs[i, 0] != self.orphandict[int(self.obcs[i, 0]) - 1, 0]): # Compare the index number in sponges to the one in the dictionary
                print("ERROR ERROR {} <-> {}".format(self.obcs[i, 0], self.orphandict[int(self.obcs[i, 0]) - 1, 0]))
            # if (i<25): print("Cell {}: {}  {}  {}".format(i+1,self.cells[i,0],self.cells[i,1],self.cells[i,2]))
            self.obcs[i, ioNode] = self.orphandict[int(self.obcs[i, ioNode]) - 1, 1]
        print("Re-indexing obcs.... DONE")
    # def reindexObcs ... END

    #
    #
    #
    def reindexOrphans(self):
        self.reindexNodes()
        self.reindexCells()
        self.reindexObcs()
        self.reindexSponges()
        self.reindexTides()
        self.reindexRivers()
    # def reindexOrphans END

    #
    #
    def reindexRivers(self):
        print("Re-indexing rivers....")
        for i in range(self.rivercount):
            # print("{} {}".format(i,self.rivers[i, irNode]))
            if (self.rivers[i, irNode] != self.orphandict[int(self.rivers[i, irNode]) - 1, 0]): # Compare the index number in rivers to the one in the dictionary
                print("ERROR RIVER REINDEX ERROR {} <-> {}".format(self.rivers[i, irNode], self.orphandict[int(self.rivers[i, irNode]) - 1, 0]))
            # if (i<25): print("rivers {}: {}".format(i+1,self.rivers[i,irNode]))
            self.rivers[i, irNode] = self.orphandict[int(self.rivers[i, irNode]) - 1, 1]
            # if (i < 25): print("rivers {}: {}".format(i + 1, self.rivers[i, irNode]))
        print("Re-indexing rivers.... DONE")
    # def reindexNodes ... END
    #
    #
    def reindexSponges(self):
        print("Re-indexing sponges....")
        for i in range(self.spongecount):
            if (self.sponges[i, 0] != self.orphandict[int(self.sponges[i, 0]) - 1, 0]): # Compare the index number in sponges to the one in the dictionary
                print("ERROR SPONGE REINDEX ERROR {} <-> {}".format(self.sponges[i, 0], self.orphandict[int(self.sponges[i, 0]) - 1, 0]))
            # if (i<25): print("sponges {}: {}  {}  {}".format(i+1,self.sponges[i,0],self.sponges[i,1],self.sponges[i,2]))
            self.sponges[i, 0] = self.orphandict[int(self.sponges[i, 0]) - 1, 1]
        print("Re-indexing sponges.... DONE")
    # def reindexNodes ... END

    #
    #
    def reindexTides(self):
        print("Re-indexing tides....")
        for i in range(self.tidecount):
            if (self.tides[i, itObcNodes] != self.orphandict[int(self.tides[i, itObcNodes]) - 1, 0]): # Compare the index number in sponges to the one in the dictionary
                print("ERROR TIDE REINDEX ERROR {} <-> {}".format(self.tides[i, itObcNodes], self.orphandict[int(self.tides[i, itObcNodes]) - 1, 0]))
            # if (i<25): print("Cell {}: {}  {}  {}".format(i+1,self.tides[i,0],self.tides[i,1],self.tides[i,2]))
            self.tides[i, itObcNodes] = self.orphandict[int(self.tides[i, itObcNodes]) - 1, 1]
        self.tidecdlfilecontent[itcObcNodes]=", ".join(str(self.tides[i,:])).strip()
        print("Re-indexing tides.... DONE")
    # def reindexNodes ... END

    def setCellsLength(self, cellcount):
        self.cellcount = cellcount
        cnt = max(0, cellcount)
        self.cells = np.zeros((cnt, iCellFieldCount),dtype=int)  # Example of file record: "     30 117215  66138  58140      1"
        self.cellCenters = np.zeros((cnt, iCellCenterFieldCount),dtype=float)  # Example of file record: "     30 117215  66138  58140      1"

    def setObcsLength(self, obccount):
        self.obccount = obccount
        cnt = max(0, obccount)
        self.obcs = np.zeros((cnt, iObcFieldCount),dtype=int)  # Example of file record: "   11   7550      1"

    def setCorsLength(self, corcount):
        self.corcount = corcount
        self.cors = np.zeros((corcount, iObcFieldCount),dtype=float)

    def setDepsLength(self, depcount):
        self.depcount = depcount
        self.deps = np.zeros((depcount, iObcFieldCount),dtype=float)

    def setNodesLength(self, nodecount):
        self.nodecount = nodecount
        cnt = max(0, nodecount)
        self.nodes = np.zeros((cnt, iNodeFieldCount),dtype=np.double)  # Example of file record: "   3164 -0.42137998E+04  0.34138398E+05  0.00000000E+00"

    def setRiversLength(self, rivercount):
        self.rivercount = rivercount
        cnt = max(0, rivercount)
        self.rivers = np.zeros((cnt, iRiverFieldCount),dtype=object)  # Example of file record: "   3164 12000.0  0.150
        self.rivers[:, 0] = ""
        self.rivers[:, 1] = ""
        self.rivers[:, 2] = ""
        self.rivers[:, irNode] = 0
        self.rivers[:, 4] = ""
        self.rivers[:, 5] = ""


    def setSpongesLength(self, spongecount):
        self.spongecount = spongecount
        cnt = max(0, spongecount)
        #self.sponges = np.zeros((cnt, iSpongeFieldCount),dtype=dtypeSponge)  # Example of file record: "   3164 12000.0  0.150
        self.sponges = np.zeros((cnt, iSpongeFieldCount),dtype=object)  # Example of file record: "   3164 12000.0  0.150
        self.sponges[:, isNode] = int(0)
        self.sponges[:, (isNode+1):] = float(0)

    def setTidesLength(self, tidecount):
        self.tidecount = tidecount
        cnt = max(0, tidecount)
        self.tides = np.zeros((cnt, iTideFieldCount),dtype=object)
        self.tides[:, itObcNodes] = int(0)

    def setOrphanDictLength(self, orphandictcount):
        self.orphandictcount = orphandictcount
        cnt = max(0,orphandictcount)
        self.orphandict = np.zeros((cnt, iOrphanDictFieldCount),
                                   dtype=int)  # Current index, new index, to be filled by checkOrphanNodes

    #
    #
    #
    def writeCorFile(self, fn):
        print("Writing cor file: {} ...".format(fn))
        s = []
        s.append("Node Number = {}\n".format(self.corcount))
        for i in range(self.corcount):
            s.append("{: .9E} {: .9E} {: .9E}\n".format(self.nodes[i, inX], self.nodes[i, inY], self.nodes[i, inCor], 1))
        s = "".join(s)
        io.writeFile(fn, s)
        print("Writing cor file: {} ... DONE".format(fn))
    #
    #
    #
    def writeDepFile(self, fn):
        print("Writing dep file: {} ...".format(fn))
        s = []
        s.append("Node Number = {}\n".format(self.corcount))
        for i in range(self.corcount):
            s.append("{: .9E} {: .9E} {: .9E}\n".format(self.nodes[i, inX], self.nodes[i, inY], self.nodes[i, inDep], 1))
        s = "".join(s)
        io.writeFile(fn, s)
        print("Writing dep file: {} ... DONE".format(fn))
    #
    #
    #
    def writeObcFile(self, fn):
        print("Writing obc file: {} ...".format(fn))
        s = []
        s.append("OBC Node Number = {}\n".format(self.spongecount))
        for i in range(self.spongecount):
            s.append("{:>6} {:>6} {:>6}\n".format(self.obcs[i, isNode], self.obcs[i, isRadius], self.obcs[i, isExp], 1))
        s = "".join(s)
        io.writeFile(fn, s)
        print("Writing obc file: {} ... DONE".format(fn))

    #
    #
    #
    def writeRiverNmlFile(self, fn,ncfilesuffix):
        print("Writing river (.nml) file: {} ...".format(fn))
        s = []
        for i in range(self.rivercount):
            s.append("{}".format(self.rivers[i, 0]))
            s.append("{}".format(self.rivers[i, 1]))
            tmp=self.rivers[i, 2].replace(".nc",ncfilesuffix+".nc")
            s.append("{}".format(tmp))
            s.append("RIVER_GRID_LOCATION   = {}".format(self.rivers[i, irNode]))
            s.append("{}".format(self.rivers[i, 4]))
            s.append("{}".format(self.rivers[i, 5]))

        s="\n".join(s)
        s=s.strip()
        io.writeFile(fn, s)
        print("Writing river (.nml) file: {} ... DONE".format(fn))
    #
    #
    #
    def writeSpgFile(self, fn):
        print("Writing spg file: {} ...".format(fn))
        s = []
        s.append("Sponge Node Number = {}\n".format(self.spongecount))
        for i in range(self.spongecount):
            s.append(sSpongeExport.format(self.sponges[i, isNode], self.sponges[i, isRadius], self.sponges[i, isExp], 1))
        s = "".join(s)
        io.writeFile(fn, s)
        print("Writing spg file: {} ... DONE".format(fn))
    #
    #
    #
    def writeTideCdlFile(self, fn):
        print("Writing tide (.cdl) file: {} ...".format(fn))
        self.tidecdlfilecontent[itcObcNodes]=u.generateDataSeries("",self.tides[:,itObcNodes],self.tidecount,1,"{:d}")
        s = "".join(self.tidecdlfilecontent)
        io.writeFile(fn, s)
        print("Writing tide (.cdl) file: {} ... DONE".format(fn))

    #
    #
    #
    def buildTideNetcdfFile(self, fn):
        fn2 = fn.replace(".cdl",".nc")
        print("Building tide (.nc) file: {} ...".format(fn2))
        print("Generating NetCDF file: {} ...".format(fn2))
        cmd = "ncgen -b {} -o {}".format(fn, fn2)
        os.system(cmd)
        print("Building tide (.nc) file: {} ... DONE".format(fn2))

    #
    #
    #
    #
    def writeGridFile(self, fn):
        print("Writing grid file: {} ...".format(fn))
        s = []
        s.append("Node Number = {}\n".format(self.nodecount))
        s.append("Cell Number = {}\n".format(self.cellcount))
        for i in range(self.cellcount):
            s.append("{:>6d} {:>6d} {:>6d} {:>6d} {:>6d}\n".format(i + 1, self.cells[i, ic1], self.cells[i, ic2],
                                                                   self.cells[i, ic3], 1))

        for i in range(self.nodecount):
            s.append(
                "{:>6d} {: .7f} {: .7f} {: .7f}\n".format(i + 1, self.nodes[i, inX], self.nodes[i, inY], self.nodes[i, inZ]))
        s = "".join(s)
        io.writeFile(fn, s)
        print("Writing grid file: {} ... DONE".format(fn))

    #
    #
    # writeOrphanDictionary
    #
    def writeOrphanDictionary(self, fn):
        s = []
        for i in range(self.nodecount):
            s.append("{:>5d} {:>5d}\n".format(self.orphandict[i, 0], self.orphandict[i, 1]))
        s = "".join(s)
        io.writeFile(fn, s)

    #
    #
    #
    def writeOrphansTxtFile(self, fn):
        io.writeFile(fn, self.orphans)






