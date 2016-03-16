# This script will download VIIRS nighttime lights TIFs for January through August 2015

cd /atlas/u/nj/viirs/2015

# Download April
cd 4/1
pwd
wget http://mapserver.ngdc.noaa.gov/viirs_data/viirs_composite/v10//201504/vcmcfg/SVDNB_npp_20150401-20150430_75N180W_vcmcfg_v10_c201506011707.tgz ./
tar -xvzf SVD*
rm *.tgz

cd ../2
pwd
wget http://mapserver.ngdc.noaa.gov/viirs_data/viirs_composite/v10//201504/vcmcfg/SVDNB_npp_20150401-20150430_75N060W_vcmcfg_v10_c201506011707.tgz ./
tar -xvzf SVD*
rm *.tgz

cd ../3
pwd
wget http://mapserver.ngdc.noaa.gov/viirs_data/viirs_composite/v10//201504/vcmcfg/SVDNB_npp_20150401-20150430_75N060E_vcmcfg_v10_c201506011707.tgz ./
tar -xvzf SVD*
rm *.tgz

cd ../4
pwd
wget http://mapserver.ngdc.noaa.gov/viirs_data/viirs_composite/v10//201504/vcmcfg/SVDNB_npp_20150401-20150430_00N180W_vcmcfg_v10_c201506011707.tgz ./
tar -xvzf SVD*
rm *.tgz

cd ../5
pwd
wget http://mapserver.ngdc.noaa.gov/viirs_data/viirs_composite/v10//201504/vcmcfg/SVDNB_npp_20150401-20150430_00N060W_vcmcfg_v10_c201506011707.tgz ./
tar -xvzf SVD*
rm *.tgz

cd ../6
pwd
wget http://mapserver.ngdc.noaa.gov/viirs_data/viirs_composite/v10//201504/vcmcfg/SVDNB_npp_20150401-20150430_00N060E_vcmcfg_v10_c201506011707.tgz ./
tar -xvzf SVD*
rm *.tgz

cd ../..