library(dplyr)
library(tidyr)

t <- read.csv(file="Q7-input-avocado.csv", header=TRUE, sep=",")
o = group_by(t, year) %>% summarise(mean = sum(Total.Volume))
o 
#write.csv(o, file="Q7-output-avocado.csv", row.names = FALSE, quote=FALSE)
