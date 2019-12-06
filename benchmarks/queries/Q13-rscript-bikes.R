library(dplyr)
library(tidyr)

t <- read.csv("Q13-input-bikes.csv")
o = group_by(t, city) %>% summarise(n = n())
o 
write.csv(o, file="Q13-output-bikes.csv", row.names = FALSE, quote=FALSE)
