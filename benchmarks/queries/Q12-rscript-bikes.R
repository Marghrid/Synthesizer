library(dplyr)
library(tidyr)

t <- read.csv("Q12-input-bikes.csv")
o = group_by(t, city) %>% summarise(n = sum(dock_count))
o 
write.csv(o, file="Q12-output-bikes.csv", row.names = FALSE, quote=FALSE)
