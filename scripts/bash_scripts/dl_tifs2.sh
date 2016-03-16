# This script will download VIIRS nighttime lights TIFs for January through August 2015

cd /atlas/u/nj/viirs/2015

# Download February
cd 2/1
pwd
wget http://mapserver.ngdc.noaa.gov/viirs_data/viirs_composite/v10//201502/vcmcfg/SVDNB_npp_20150201-20150228_75N180W_vcmcfg_v10_c201504281504.tgz ./
tar -xvzf SVD*
rm *.tgz

cd ../2
pwd
wget http://mapserver.ngdc.noaa.gov/viirs_data/viirs_composite/v10//201502/vcmcfg/SVDNB_npp_20150201-20150228_75N060W_vcmcfg_v10_c201504281504.tgz ./
tar -xvzf SVD*
rm *.tgz

cd ../3
pwd
wget http://mapserver.ngdc.noaa.gov/viirs_data/viirs_composite/v10//201502/vcmcfg/SVDNB_npp_20150201-20150228_75N060E_vcmcfg_v10_c201504281504.tgz ./
tar -xvzf SVD*
rm *.tgz

cd ../4
pwd
wget http://mapserver.ngdc.noaa.gov/viirs_data/viirs_composite/v10//201502/vcmcfg/SVDNB_npp_20150201-20150228_00N180W_vcmcfg_v10_c201504281504.tgz ./
tar -xvzf SVD*
rm *.tgz

cd ../5
pwd
wget http://mapserver.ngdc.noaa.gov/viirs_data/viirs_composite/v10//201502/vcmcfg/SVDNB_npp_20150201-20150228_00N060W_vcmcfg_v10_c201504281504.tgz ./
tar -xvzf SVD*
rm *.tgz

cd ../6
pwd
wget http://mapserver.ngdc.noaa.gov/viirs_data/viirs_composite/v10//201502/vcmcfg/SVDNB_npp_20150201-20150228_00N060E_vcmcfg_v10_c201504281504.tgz ./
tar -xvzf SVD*
rm *.tgz

cd ../..