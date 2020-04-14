## Script for creating city-scale simulated data for testng

# This script takes the simulated datasets at https://zenodo.org/record/2865830#.XoZqadMzaSM and converts them into a format that mimic the data being used by Privte Kit Safe Paths for purposes of testing.

library(tidyverse)

# reading data downloaded from Zenodo, then converting time to the milisecond unix time used in the Safe Paths exports and fixing typo in the latitude variable name.
D = as_tibble(readRDS("~/Downloads/buffalo_sim_full.Rds")) %>% mutate(time= as.numeric(as.POSIXct("2020-04-10 8:00:00 EST"))*1000 + (time*60*60*1000), latitude=latitute) %>% select("latitude", "longitude", "time", "ID")

# saving the whole thing as csv
write_csv(D, path="~/projects/covid19_sim_data/buffalo_sim_full.csv")
