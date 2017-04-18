#!/usr/bin/python3
# Script to quickly plot line curves from tabulated data
# Author Roelof Rietbroek (http://wobbly.earth)
# initial version 7 March 2017
# License: see file LICENSE (MIT) 
import sys
from optparse import OptionParser
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
#main plotting function
def main(argv):
	#set up command line options
	usage=argv[0]+ " [Options] [FILES]\n"\
		+"Plot lines from tabulated ascii data (file or standard input)\n"\
		+"if no FILES are specified the script reads from standard input\n"\
		+"FILES may also contain one instance of '-' (standard input)"
		
	parser=OptionParser(usage)
	parser.add_option("-s","--skip",metavar="NSKIP",default=0,type="int",help="skip NSKIP header lines in the input file(s)")
	parser.add_option("-l","--legend",type="string",metavar="LEGEND",help="Make a legend for the plot by specifying LEGEND as: Curve1/Another Curve/..")	
	parser.add_option('-c','--columns',type="string",metavar="COLS",help="only print specific columns from the files e.g. COLS: 2/6/8, the default prints all columns in all files")
	parser.add_option('-x',"--xlabel",type="string",help="Specify a label to put on the x axis")
	parser.add_option('-y',"--ylabel",type="string",help="Specify a label to put on the y axis")
	parser.add_option('-t',"--title",type="string",help="Add a title to the plot")
	parser.add_option('-o',"--output", metavar="IMAGE", type="string",help="Output the plot to an image rather than a dynamic viewer. Suffices (e.g. .pdf, .eps, .svg, .png) are automatically detected from IMAGE but must be supported by the matplotlib backend)")
	parser.add_option('--transparency',action="store_true",help="Set the background to be transparent")
	#parser.add_option('--mat',type="string",default="NOMAT",metavar="VAR",help="Input file is a matlab file. Plot the data from matrixvariable VAR)")
	#parser.add_option('--listmat',action="store_true",help="List available variables from the input matlab files")	
        
	parser.add_option('-m',"--multiply",type="float",default=1.0,metavar="SCALE", help="multiply the Y values with SCALE")	
	parser.add_option('-g',"--grid",action="store_true",help="show grid on the plot")
	
	(options, args) = parser.parse_args()
	fids=[]
	
	matlab=False
	#if options.mat != "NOMAT" or options.listmat:
    #        matlab=True
	
	#if matlab and not args:
    #        print("Sorry: Matlab files cannot be read from standard input",file=sys.stderr)
    #        sys.exit(1)
	#if matlab and len(args)!=1:
	#	print("Only 1 input file allowed for matlab data",file=sys.stderr)
	#	sys.exit(1)

#	if options.listmat:
#		tmp=sio.whosmat(args[0])
#		for var in tmp:
#			print("variable %s"%var[0],file=sys.stdout,end="")
#			print(var[1],file=sys.stdout)
#		sys.exit(0)

	#read in file(s)
	if not args:
		#read from standard input
		nfiles=1
		fids.append(sys.stdin)
	elif not matlab:
		#assume the remaining input arguments are files
		for f in args:
			if f == "-":
				fids.append(sys.stdin)
			else:
				fids.append(open(f,'r'))	

	data=[]
	for fid in fids:
		#possibly skip some lines
		for i in range(options.skip):
			fid.readline()
		datatmp=[]
		for ln in fid.readlines():
			fspl=ln.split()
			#append the rest 
			datatmp.append([float(i) for i in fspl]) 

		#append the data to the collection as a numpy array
		data.append(np.array(datatmp))
		#close the file
		fid.close()
	
	if options.columns:
		columns=[int(i)-1 for i in options.columns.split('/')]
	else:
	#plot all columns(max 200) starting from 1
		columns=[i for i in range(1,200)]

	
	if options.legend:
		labels=options.legend.split('/')
		label=iter(labels)
	else:
		labels=[]

	if options.multiply:
		for i in range(len(fids)):
			data[i][:,1:]*=options.multiply
	#do some plotting
	fig=plt.figure()
	
	for i in range(len(fids)): 
		for col in range(data[i].shape[1]):
			if not col in columns:
				continue
				
			if labels:
				try:
					plt.plot(data[i][:,0],data[i][:,col],label=next(label))
				except StopIteration:
					print("Sorry: run out of labels for the legend",file=sys.stderr)
					sys.exit(1)
			else:	
				plt.plot(data[i][:,0],data[i][:,col])
	#add axis labels
	if options.xlabel:
		plt.xlabel(options.xlabel)
	if options.ylabel:
		plt.ylabel(options.ylabel)

	#add title
	if options.title:
		plt.title(options.title)

	#create a legend
	if labels:
		plt.legend(loc='best')

	if options.grid:
		plt.grid()
	#print or show the figure
	if options.output:
		plt.savefig(options.output,transparent=options.transparency)
	else:
		plt.show()



if __name__ == "__main__":
	main(sys.argv)
