# TSX Scripts

Scripts in this directory are helpful for processing TerraSAR-X (TSX) data with ROI_PAC

## TSX Pre-processor
Unlike other satellites, skip generating raw files and go straight to slc files. [Walter Szeliga](http://www.geology.cwu.edu/facstaff/walter) has made code available that reads the raw formats of current satellites (TSX, CSK, RS2). You must run this code before proceeding with ROI_PAC. 

The [GMTSAR website](http://topex.ucsd.edu/gmtsar/downloads/) also has a modified version of the pre-processors that work with GMTSAR. The following notes are for using the version downloaded via the version posted on this page.

```
wget https://github.com/scottyhq/insar_scripts/raw/branch/sar-0.5.tar.gz
tar -xzvf sar-0.5.tar.gz
cd sar-0.5
./configure
make install
```

##### Troubleshooting install on Ubuntu Linux
In order to successfully install the pre-processors on a lab computer we had to install additional libraries and modify the configure step to find them:

```
apt-get install libtiff-dev libboost-all-dev libhdf5-dev

./configure --with-boost-libdir=/usr/lib/x86_64-linux-gnu --prefix=/home/mpguest/MY_BIN LDFLAGS='-L/usr/lib/x86_64-linux-gnu -L/home/mpguest/miniconda/lib' CPPFLAGS='-I/home/mpguest/miniconda/include' LIBS='-lhdf5 -lhdf5_cpp'
```

Also, compiling the TSX preprocessor required commenting out the following lines in `tsx/src/Header.cpp` (59,60,95,96):

```
std::string formatCheck("CSAR");
if (formatCheck.compare(format) != 0) {throw "Not a valid COSAR file";}
```

You can do this automatically with a tricky command `sed -i 's,.*SAR.*,//&,g' Header.cpp`

Finally, I had to add a flag `-std=c++0x` when the following TSX portion of the code failed:

```
g++ -std=c++0x -DHAVE_CONFIG_H -I. -I..  -I../include -I.. -I../../libsar/include -I../../tinyxpath/include -I/usr/include -I/home/mpguest/miniconda/include  -g -O2 -MT make_slc_tsx.o -MD -MP -MF .deps/make_slc_tsx.Tpo -c -o make_slc_tsx.o make_slc_tsx.cpp
```


##### Troubleshooting install on MacOSX
In order to install the pre-processor successfully on my computer I had to download a few libraries and then point to their location at the configure step:

```
brew install boost
brew install hdf5 --enable-cxx
./configure --with-boost=/usr/local/Cellar/boost/1.55.0 CPPFLAGS=-I/usr/local/include LDFLAGS=-L/usr/local/lib --prefix=/Users/scott/Software/ROI_PAC_3_0_1/sar-0.5
make install
```

##### Create SLCs

Be sure to add the pre-processor exectuables to your search path `export PATH=$PATH:[rootdir]/sar-0.5/bin` and then try running:

```
tar -xzvf dims_op_oc_dfd2_372011900_1.tar.gz
make_slc_tsx -i dims_op_oc_dfd2_372011900_1/TSX-1.SAR.L1B/TDX1_SAR__SSC______SM_S_SRA_20111024T230132_20111024T230140/TDX1_SAR__SSC______SM_S_SRA_20111024T230132_20111024T230140.xml -p 111024
```

## Prepare_tsx.py
Assuming you've ordered data through the German Aerospace Center (DLR) [Web Portal](https://centaurus.caf.dlr.de:8443/eoweb-ng/template/default/welcome/entryPage.vm) you should have a few tar.gz files in a directory. Running this script will unarchive the data, and automatically create the required directory structure for processing with ROI_PAC. Note that this requires TSX pre-processor scripts (above) to be installed.


## Running ROI_PAC
The standard process_2pass.pl script has to be *run in two steps*:
```
process_2pass.pl int.proc roi_prep orbbase
process_2pass.pl int.proc slcs done_sim_removal
```


## Different PRFs
TSX/TDX data tends to have PRFs that can vary by >100Hz. This causes a linear change in azimuth offsets, so if you have to run ampcor manually be sure to find the offset towards the top of your SLC file and use the **rds** specifier:

```
ampcor ampcor.in rds > ampcor.out
```
