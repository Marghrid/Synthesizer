library(dplyr)
library(tidyr)

t <- read.csv("Q11-input-titanic.csv")
o = filter(t, Survived == 1) %>% group_by(Parch) %>% summarise(n = n())
o 
#write.csv(o, file="Q11-output-titanic.csv", row.names = FALSE, quote=FALSE)
