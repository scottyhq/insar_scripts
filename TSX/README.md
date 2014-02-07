# TSX Scripts

Scripts in this directory are helpful for processing TerraSAR-X (TSX) data with ROI_PAC

## prepare_tsx.py
Assuming you've ordered data through the German Aerospace Center (DLR) [Web Portal](https://centaurus.caf.dlr.de:8443/eoweb-ng/template/default/welcome/entryPage.vm) you should have a few tar.gz files in a directory. Running this script will unarchive the data, and automatically create the required directory structure for processing with ROI_PAC. Unlike other satellites, we skip generating raw files and go straight to slc files. The included programs in the tsx_parser/ folder accomplish this.

```
export TSX_DIR=/path/to/tsx_parser
cd /data/TSX/o134/
prepare_tsx.py
```
