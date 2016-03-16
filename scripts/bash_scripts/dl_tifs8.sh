# This script will download VIIRS nighttime lights TIFs for January through August 2015

cd /atlas/u/nj/viirs/2015

# Download August
cd 8/1
pwd
wget http://mapserver.ngdc.noaa.gov/viirs_data/viirs_composite/v10//201508/vcmcfg/SVDNB_npp_20150801-20150831_75N180W_vcmcfg_v10_c201509301759.tgz ./
tar -xvzf SVD*
rm *.tgz

cd ../2
pwd
wget http://mapserver.ngdc.noaa.gov/viirs_data/viirs_composite/v10//201508/vcmcfg/SVDNB_npp_20150801-20150831_75N060W_vcmcfg_v10_c201509301759.tgz ./
tar -xvzf SVD*
rm *.tgz

cd ../3
pwd
wget http://mapserver.ngdc.noaa.gov/viirs_data/viirs_composite/v10//201508/vcmcfg/SVDNB_npp_20150801-20150831_75N060E_vcmcfg_v10_c201509301759.tgz ./
tar -xvzf SVD*
rm *.tgz

cd ../4
pwd
wget http://mapserver.ngdc.noaa.gov/viirs_data/viirs_composite/v10//201508/vcmcfg/SVDNB_npp_20150801-20150831_00N180W_vcmcfg_v10_c201509301759.tgz ./
tar -xvzf SVD*
rm *.tgz

cd ../5
pwd
wget http://mapserver.ngdc.noaa.gov/viirs_data/viirs_composite/v10//201508/vcmcfg/SVDNB_npp_20150801-20150831_00N060W_vcmcfg_v10_c201509301759.tgz ./
tar -xvzf SVD*
rm *.tgz

cd ../6
pwd
wget http://mapserver.ngdc.noaa.gov/viirs_data/viirs_composite/v10//201508/vcmcfg/SVDNB_npp_20150801-20150831_00N060E_vcmcfg_v10_c201509301759.tgz ./
tar -xvzf SVD*
rm *.tgz

cd ../..


