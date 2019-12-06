library(dplyr)
library(tidyr)

t <- read.csv("Q9-input-titanic.csv")
o = filter(t, Survived == 1) %>% group_by(Sex) %>% summarise(n = n())
o 
#write.csv(o, file="Q9-output-titanic.csv", row.names = FALSE, quote=FALSE)
