# TSX Scripts

Scripts in this directory are helpful for processing TerraSAR-X (TSX) data with ROI_PAC

## TSX Pre-processor
Unlike other satellites, skip generating raw files and go straight to slc files. Walter Szeliga has made code available that reads the raw formats of current satellites (TSX, CSK, RS2). You must run this code before proceding with ROI_PAC. Download the software via the [GMTSAR website](http://topex.ucsd.edu/gmtsar/downloads/), or follow the commands below:

```
mkdir sar-0.5
cd sar-0.5
wget http://topex.ucsd.edu/gmtsar/tar/sar-0.5.tar
tar -xvf sar-0.5.tar
cd sar-0.5
./configure
make install
```

##### Note on installing on MacOSX
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

## prepare_tsx.py
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
