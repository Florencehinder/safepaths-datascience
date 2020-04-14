# simple script for visualizing Private Kit paths in R

library(jsonlite)
library(tidyverse)
library(ggmap)

# set this to the name of the file exported from Private Kit
my_track = "1586439375854.json"

# reads and converts to tibble
D = as_tibble(fromJSON(txt=my_track))

# plots on map. (You may need to play with the zoom value depending on how big your track is.)
qmplot(longitude, latitude, data = D, maptype = "toner-lite", color = I("red"), zoom=18) + geom_line()