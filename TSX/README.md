# TSX Scripts

Scripts in this directory are helpful for processing TerraSAR-X (TSX) data with ROI_PAC

## tsx_parser
Unlike other satellites, skip generating raw files and go straight to slc files. The included programs in the tsx_parser/ folder accomplish this.

```
tar -xzvf tsx_parser.tar.gz
cd tsx_parser/src
make
cd ../
mv src/doppler src/cosar get_height.pl make_slc_tsx.csh $MY_BIN
```

## prepare_tsx.py
Assuming you've ordered data through the German Aerospace Center (DLR) [Web Portal](https://centaurus.caf.dlr.de:8443/eoweb-ng/template/default/welcome/entryPage.vm) you should have a few tar.gz files in a directory. Running this script will unarchive the data, and automatically create the required directory structure for processing with ROI_PAC. Note that this requires tsx_parser scripts (above) to be installed.

## run ROI_PAC
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
