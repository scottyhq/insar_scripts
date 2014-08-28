#!/usr/bin/perl
### get_SRTM.pl

# 10/01/2010: Downloaded from ROIPAC wiki
#             ftp://www.geo.cornell.edu/pub/rlohman/get_SRTM.pl
#             Limitation: Worked only up to 2x2 tiles
#                         Had accss to only SRTM3
# 10/15/2010: Oh-ig Kwoun, JPL
#             Fixed coordinate orientation error
#             Fixed debugging statements
#             Added option to search for public SRTM1 DEMs over US
#             Works for any # of tiles
#             Warning: .rsc keyword/value for X_,Y_UNIT, Z_OFFSET, Z_SCALE, PROJECTION 
#                      require confirmation
# 2011/01/26: Sang-Ho Yun, JPL
#             Removed redundancy of single row/column at each
#             tile boundary in SRTM DEMs (Look for SHY)
#             with help provided by Walter Szeliga, JPL
# 2011/11/11: Sven Borgstrom, INGV
#             Row 155:  from `rm tmp`; to `rm tmp *.hgt *.hgt.zip`;
#                       to remove all the SRTM tiles after processing;
#             Last row: added to remove also the *.dem.rsc.hst file;
#                       if you need it, just comment (#) or delete the last row.            
# 2012/02/19: Rowena Lohman
#             added loop that also seeks filenames with *hgt.zip rather than *.hgt.zip
#             since SRTM tiles are stored that way for some high-latitude tiles.  Commented 
#             out automatic deletion of all .hgt files since that can be dangerous.
#             Note: original version didn't have single pixel redundancy - someone else
#             commented it out for some reason.  SHY fix has same effect as original
#             version, just with a fseek instead of a junk variable for that pixel.
#             also switched so that it writes zeros to file for open water tiles.  
#             Previously would paste copies of other files in that region.
# 2014/01/01: Scott Henderson
# 			  Changed default server to get VOID-filled version 3 SRTM from LPDAAC datapool
# 			  This dataset (SRTM plus) was released 10/20/2013
# 2014/08/20: Joey Durkin
#             Added a block that checks if the hgt.zip file already exists in the local directory,
#             and if it does then it will use that instead of downloading it from SRTM.
#             Useful for creating a mosaic of hgt files north of 60 degrees.
#			  
$] >= 5.004 or die "Perl version must be >= 5.004 (Currently $]).\n";

use Env qw(INT_SCR);
use lib "$INT_SCR";		#### Location of Generic.pm
use POSIX qw(ceil floor);
use Generic;

$argcnt=$#ARGV + 1;
if ( $argcnt < 7 ) {
  print "\n";
  print "Usage: get_SRTM.pl <output_dem_name>.dem min_lat max_lat min_lon max_lon byteswap source\n";
  print "\t<output_dem_name>.dem : output DEM filename MUST have <.dem> extension\n";
  print "\tbyteswap:  [0] No - if you do not have <byte-swap> executable\n";
  print "\t           [1] little-endian (Linux)\n";
  print "\tsource:    [1] SRTM1 30m, US\n";
  print "\t           [3] SRTM3 90m, Global\n";
  print "\n";
  die "# of arguments is WRONG\n";
}

$outfile=shift;
$lat1=shift;
$lat2=shift;
$lon1=shift;
$lon2=shift;
#$swap=shift or $swap=0;
$swap=shift;
$source=shift or $source=1;

if ($source eq 3) {
#  @dirs=("Africa","Australia","Eurasia","Islands","North_America","South_America");
	$type='SRTMGL3'
} else {
	$type='SRTMUS1'
#  @dirs=("Region_01", "Region_02","Region_03","Region_04","Region_05","Region_06","Region_07");
}

if ($lon1>180 or $lon2>180) {
  print "\n";
  die "Use lons in -180 to 180 mode\n";
}

if (($lat1<=0 && $lat2>=0) or ($lon1<=0 && $lon2>=0) or ($lon2<$lon1)) {
  print "\n";
  die "Not ready for boxes that cross equator or prime meridians\n";
}

$lat1=floor($lat1);
$lat2=ceil($lat2);
$lon1=floor($lon1);
$lon2=ceil($lon2);

$minlon=$lon1;
$maxlat=$lat2;

$dlat=$lat2-$lat1;
$dlon=$lon2-$lon1;

if ($lat1<0) {
  $latpre="S";
} else {
  $latpre="N";
}
if ($lon1<0) {
  $lonpre="W";
} else {
  $lonpre="E";
}

$byte_size=2; # short integer

if ($source eq 3) { $n=1200; } # SHY: 1201 -> 1200
if ($source eq 1) { $n=3600; } # SHY: 3601 -> 3600 

$zeros = pack("n[$n]",0);

print "$dlat by $dlon tiles requested\n";
open(OUT,">$outfile") or die "Can't open $outfile for writing\n";

for ($i=$dlat-1;$i>=0;$i--) 
{
	$a=abs($lat1+$i);  
	#print "$dlon\n"; 	
	
	for ($j=0;$j<$dlon;$j++) 
	{
		#print "$j\n";
		$b=abs($lon1+$j);
		
		
		# DON'T DOWNLOAD, file exists - Added by JD
		$file=sprintf("%s%02d%s%03d.hgt",$latpre,$a,$lonpre,$b);
		if (-e $file) 
		{
			print "$file found in local directory, skipping download\n";   
			$found[$j]=1;
			open $IN[$j], "$file" or die "Can't open $file for reading\n";
        }
		
		else
		{   # DOWNLOAD FILE
			$file=sprintf("%s%02d%s%03d.%s.hgt.zip",$latpre,$a,$lonpre,$b,$type);
            #print "$file \n";
		    $found[$j]=0;
			unless (-e $file)
			{	
				$cmd = "curl -s http://e4ftl01.cr.usgs.gov/SRTM/$type.003/2000.02.11/$file --fail -o $file";
				print "$cmd\n";
				system($cmd);
			}		

		    if ($?==0) 
		    {	print "downloaded $file\n";
			    $found[$j]=1;
			    `unzip $file`;
			    $file=sprintf("%s%02d%s%03d.hgt",$latpre,$a,$lonpre,$b); #unzipped file
			    open $IN[$j], "$file" or die "Can't open $file for reading\n";
      	    }
		    else 
			{print "downloading $file failed! assuming open water\n"; 
			} 
  		}
	}
}

	
	for ($j=0;$j<$n;$j++) {
    	for ($k=0;$k<$dlon;$k++) {
      		if($found[$k]==0) {
				print OUT "$zeros";
      		}
  			else{
				read $IN[$k],$num,$n*$byte_size;
				seek $IN[$k],$byte_size,1;    # SHY: added this line
				#     read $IN[$k],$jnk,$byte_size;  # why ??
				print OUT "$num";  
      		}
      		#    print OUT "$jnk";
    	}
  	}
  	if ($i>0) {
    	for ($k=0;$k<$dlon;$k++) {
      		close $IN[$k];
    	}
  	}


  
#for ($k=0;$k<$dlon;$k++) {   # why??
#  read $IN[$k],$num,$n*$byte_size;
## read $IN[$k],$jnk,$byte_size; 
#  close $IN[$k];
#  print OUT "$num";
#}
#print OUT "$jnk";

close(OUT);
if ($swap) {
  `mv $outfile tmp`;
  `byte-swap 2 < tmp > $outfile`;
  #`rm tmp *hgt *hgt.zip`; #commented this out since it was dangerous - people may have .hgt files they don't want to delete
}

# original
#$width=$n*$dlat+1;
#$length=$n*$dlon+1;
$width=$n*$dlon;
$length=$n*$dlat;
if ($source eq 3) {
  $dx=0.00083333333333;
  $dy=-0.00083333333333;
} else {
  $dx=0.00083333333333/3;
  $dy=-0.00083333333333/3;
}
$x1=$minlon;  # SHY: removed -$dx/2
$y1=$maxlat;  # SHY: removed +$dy/2
Use_rsc "$outfile write WIDTH $width";
Use_rsc "$outfile write FILE_LENGTH $length";
Use_rsc "$outfile write X_STEP $dx";  # longitude
Use_rsc "$outfile write Y_STEP $dy";  # latitude
Use_rsc "$outfile write X_FIRST $x1";
Use_rsc "$outfile write Y_FIRST $y1";

# ohig: to make it compatible with other existing DEM .rsc file
#       This section is TBC
Use_rsc "$outfile write X_UNIT        degres";
Use_rsc "$outfile write Y_UNIT        degres";
Use_rsc "$outfile write Z_OFFSET      0";
Use_rsc "$outfile write Z_SCALE       1";
Use_rsc "$outfile write PROJECTION    LATLON";

`rm *.dem.rsc.hst`;
