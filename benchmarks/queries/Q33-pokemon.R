library(dplyr)
library(tidyr)

t <- read.csv("Q33-input-pokemon.csv")
o =  group_by(t, Generation) %>% summarize(n = n())
o 
#write.csv(o, file="Q33-output-pokemon.csv", row.names = FALSE, quote=FALSE)
