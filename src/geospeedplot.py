#!/usr/bin/env python3
#python script to quickly plot geographical grids 
# Author Roelof Rietbroek (http://wobbly.earth)
# initial version 5 December 2017
# License: see file LICENSE (MIT) 
#part of speedplot
import sys
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from optparse import OptionParser
from netCDF4 import Dataset
import numpy as np
import re
def main(argv):


#set up command line options
    usage=argv[0]+ " [Options] NCFILE\n"\
            +"Plot geographical grids from netcdf file (NCFILE) and possibly points\n"
            
    parser=OptionParser(usage)
    parser.add_option("-V","--Var",metavar="VAR[N]",default='z[0]',type="string",help="specify the netcdf variable name and layer to plot ")
    # parser.add_option("-l","--legend",type="string",metavar="LEGEND",help="Make a legend for the plot by specifying LEGEND as: Curve1/Another Curve/..")	
    parser.add_option('-z',"--zlabel",type="string",default="",help="Specify a label to put on the color (z) axis")
    parser.add_option('-r',"--range",type="string",metavar="ZMIN,ZMAX",help="set range of colorbar")
    parser.add_option("--cmap",default="viridis",metavar="COLORMAP",help="Set colormap name")
    parser.add_option('-t',"--title",type="string",help="Add a title to the plot")
    parser.add_option('-o',"--output", metavar="IMAGE", type="string",help="Output the plot to an image rather than a dynamic viewer. Suffices (e.g. .pdf, .eps, .svg, .png) are automatically detected from IMAGE but must be supported by the matplotlib backend)")
    parser.add_option('--transparency',action="store_true",help="Set the background to be transparent")
    parser.add_option('-m',"--multiply",type="float",default=1.0,metavar="SCALE", help="multiply the grid and symbols values with SCALE")	
    
    #parser.add_option('-g',"--grid",action="store_true",help="show grid on the plot")
    parser.add_option('-p',"--projection",type="string",metavar="PROJ",default='glob180',help="choose projection:\n"\
            +"glob(global equidist centered on 0 deg meridian), glob180 (centered on 180 deg meridian)")
    parser.add_option('-s',"--symbols",type="string",metavar="LONLATVALUEFILE",help="Plot symbols at lon lat positions with color proportional to value") 
    
    (options, args) = parser.parse_args()
    fids=[]
	
    if not args:
        grdfile=[]
        if not options.symbols:
            print("Error: no netcdf file or lonlat file given",file=sys.stderr)
            parser.print_help()
            sys.exit(1)
    else:
        grdfile=args[:][0]
    
    if grdfile:
     #open netcdf data file
        print(grdfile)
        ncid=Dataset(grdfile,'r')
        ncid.set_auto_mask(False)
        #try to read in longitude and latitude
        for latname in ["y","latitude","Latitude","lat"]:
            try:
                lat=ncid[latname][:]
                break
            except: 
                 pass
        if not lat.any():
            print("couldn't find a suitable latitude variable",file=sys.stderr)
            sys.exit(1)

        for lonname in ["x","longitude","Longitude","lon"]:
            try:
                lon=ncid[lonname][:]
                break
            except: 
                 pass
        if not lon.any():
            print("couldn't find a suitable longitude variable",file=sys.stderr)
            sys.exit(1)

        #load gridvariable
        try:
            ztpl=re.findall('(.*?)\[(.*?)\]',options.Var)
            if ztpl:
                name=ztpl[0][0]
                dim=int(ztpl[0][1])
            else:
                name=options.Var
                dim=0
            z=options.multiply*ncid[name][:]

            if z.ndim ==3:
                z=z[dim]

        except:
            print("cannot load %s"%options.Var,file=sys.stderr)
            sys.exit(1)
        ncid.close() 
    
    if options.symbols:

        #read station name and position
        plon=[]
        plat=[]
        pval=[]
        fid=open(options.symbols,'r')
        for ln in fid.readlines():
            lspl=ln.split()
            plon.append(float(lspl[0]))
            plat.append(float(lspl[1]))
            if len(lspl) ==3:
                pval.append(float(lspl[2]))
        fid.close()

    fromproj=ccrs.PlateCarree(central_longitude=0)
    if options.projection == 'glob':
        #make a global plot centered on the 0 meridian
        proj=ccrs.PlateCarree(central_longitude=0)
    elif options.projection == 'glob180':
        proj=ccrs.PlateCarree(central_longitude=180.0)
        # if options.symbols:
        #     for i in range(len(plon)):
        #         if plon[i] < 0:
        #             plon[i]=360+plon[i]
        #
    
    ax=plt.axes(projection=proj)

    if grdfile:
        #plot the gridded data
        if options.range:

            spltrng=[float(x) for x in options.range.split(',')]
            plt.contourf(lon, lat, z,20, transform=fromproj,vmin=spltrng[0],vmax=spltrng[1],cmap=options.cmap)
        else:
            plt.contourf(lon, lat, z, 20,transform=fromproj,cmap=options.cmap)


        #colorbar drawing (horizontal)
        cbarw=0.03
        axpos=ax.get_position()
        cbar_ax = plt.gcf().add_axes([axpos.x0,axpos.y0-cbarw*1.5,axpos.width,cbarw])
        cbar=plt.colorbar(label=options.zlabel,cax=cbar_ax,orientation='horizontal')
    
    ax.coastlines()

    # if options.symbols:
    #     # print(min(plon),min(plat),min(pval),file=sys.stderr)
    #
    #     if pval:
    # # #plot symbols on top
    #         if options.range:
    #             spltrng=[float(x) for x in options.range.split(',')]
    #             # m.scatter(plon,plat,c=pval,vmin=spltrng[0],vmax=spltrng[1],cmap=options.cmap)
    #         else:
    #             m.scatter(plon,plat,c=pval)
    #         if not cbar:
    #             m.colorbar(label=options.zlabel,cmap=options.cmap)
    #
    #     else:
    #         m.scatter(plon,plat)


	#add title
    if options.title:
        plt.sca(ax)
        plt.title(options.title)

#print or show the figure
    if options.output:
        plt.savefig(options.output,bbox_inches='tight',transparent=options.transparency)
    else:
        plt.show()


if __name__ == "__main__":
    main(sys.argv)
