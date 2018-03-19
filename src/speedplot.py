#!/usr/bin/python3
# Script to quickly plot line curves from tabulated data
# Author Roelof Rietbroek (http://wobbly.earth)
# initial version 7 March 2017
# License: see file LICENSE (MIT) 
import sys
from optparse import OptionParser
import numpy as np
import matplotlib.pyplot as plt
from cycler import cycler

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
	parser.add_option('-m',"--multiply",type="string",metavar="SCALE1/SCALE2/..", help="multiply the Y columns with SCALE1/SCALE2/..")	
	#parser.add_option('--mat',type="string",default="NOMAT",metavar="VAR",help="Input file is a matlab file. Plot the data from matrixvariable VAR)")
	#parser.add_option('--listmat',action="store_true",help="List available variables from the input matlab files")	
	parser.add_option('-a',"--aspect",type="float",default=0.5,help="Set aspect ratio of the figure")
        
	parser.add_option("--xlim",type="string",metavar="XSTART/XEND", help="Set the limits of the X axis")	
	parser.add_option("--ylim",type="string",metavar="YSTARTLEFT/YENDLEFT[/YSTARTRIGHT/YENDRIGHT]", help="Set the limits of the Y axis")	
	parser.add_option('-g',"--grid",action="store_true",help="show grid on the plot")
	parser.add_option('--twin',type="string",metavar='L/R/R/...',help="Create a plot with 2 Y axis systems, and assign the column to either the left(L) or right (R) axis")	
	parser.add_option('--mean',action="store_true",help="remove the mean from the time series before plotting")
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
	xdat=[]
	for fid in fids:
		#possibly skip some lines
		for i in range(options.skip):
			fid.readline()
		datatmp=[]
		xdattmp=[]
		for ln in fid.readlines():
			fspl=ln.split()
			xdattmp.append(float(fspl[0]))
			#append the rest 
			datatmp.append([float(i) for i in fspl[1:]]) 
		#append the data to the collection as a numpy array
		xdat.append(np.array(xdattmp))
		data.append(np.array(datatmp))
		
		#close the file
		fid.close()
	
	if options.columns:
		columns=[int(i)-2 for i in options.columns.split('/')]
	else:
	#plot all columns(max 200) starting from 1
		columns=[i for i in range(200)]
	#remove the mean from all columns
	if options.mean:
		for i in range(len(data)):
			data[i]-=data[i].mean(axis=0)



	if options.legend:
		labels=options.legend.split('/')
		label=iter(labels)
	else:
		labels=[]

	if options.multiply:
		#parse input parameter
		if options.multiply.count('/') == 0:
			scales=iter([float(options.multiply) for i in range(100)])
		else:
			scales=iter([float(i) for i in options.multiply.split('/')])
		for i in range(len(fids)):
			for col in range(data[i].shape[1]):
				if not col in columns:
					continue
				try:
					data[i][:,col]*=next(scales)
				except StopIteration:
					print("Sorry: run out of scale factors",file=sys.stderr)
					sys.exit(1)

    	#do some plotting
	fig=plt.figure()
	axislr={}
	axislr['L']=fig.gca()
	if options.twin:
		twinaxis=[i for i in options.twin.split('/')]
		axislr['R']=axislr['L'].twinx()
		#shift the color cycle of the twin axis
		cyc=axislr['R']._get_lines.prop_cycler
		[next(cyc) for i in range(0,twinaxis.count('L'))]
	else:
		twinaxis='L'*200
		# print(columns)	
	axit=iter(twinaxis) 
	for i in range(len(fids)):
		for col in range(data[i].shape[1]):
			if not col in columns:
				continue
				
			if labels:
				try:
					axislr[next(axit)].plot(xdat[i],data[i][:,col],label=next(label))
				except StopIteration:
					print("Sorry: run out of labels for the legend",file=sys.stderr)
					sys.exit(1)
			else:	
				axislr[next(axit)].plot(xdat[i],data[i][:,col])
	#add axis labels
	if options.xlabel:
		plt.xlabel(options.xlabel)


	if options.ylabel:
		if options.twin:
			ylab=options.ylabel.split('/')
			axislr['L'].set_ylabel(ylab[0])
			if len(ylab)==2:
				axislr['R'].set_ylabel(ylab[1])

		else:
			axislr['L'].set_ylabel(options.ylabel)

	#add title
	if options.title:
		plt.title(options.title)

	#create a legend
	if labels:
		if options.twin:
			axislr['L'].legend(loc='upper left')
			axislr['R'].legend(loc='upper right')
		else:
			axislr['L'].legend(loc='best')

    #possbily set aspect ratio
	if options.aspect:
		axislr['L'].set_aspect(options.aspect)
		if options.twin:
			axislr['R'].set_aspect(options.aspect)


	#Possibly set axis limits
	if options.xlim:
		xlims=[ float(x) for x in  options.xlim.split('/')]
		axislr['L'].set_xlim(xlims[0],xlims[1])

	if options.ylim:
		ylims=[float(x) for x in options.ylim.split('/')]
		if options.twin:
			axislr['L'].set_ylim(ylims[0],ylims[1])
			axislr['R'].set_ylim(ylims[2],ylims[3])
		else:
			axislr['L'].set_ylim(ylims[0],ylims[1])


	if options.grid:
		plt.grid()

	plt.tight_layout()
	#print or show the figure
	if options.output:
		plt.savefig(options.output,bbox_inches='tight',transparent=options.transparency)
	else:
		plt.show()



if __name__ == "__main__":
	main(sys.argv)
