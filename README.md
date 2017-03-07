#python3 script to quickly plot tabulated data using matplotlib

##Installation and usage
1. Install  matplotlib for python3
2. Put the script somewhere in your PATH
3. See speedplot.py --help for detailed usage

For example to plot the newest sea level curve of the Colorado Sea level group in a svg file use:
```wget -O - http://sealevel.colorado.edu/files/2016_rel4/sl_ns_global.txt | speedplot.py -s 1 -x years -y "mm of sea level" -t "Global mean sea level from CU sea level Research group" -o GMSL.svg```

which will result in something like this:

![Global mean sea level from altimetry (data courtesy CU group)](/example/GMSL.png?raw=true "Global Mean Sea Level")

### Things to do
* Customized colorschemes?
* Plot markers, errorbars
* Adding subplots




