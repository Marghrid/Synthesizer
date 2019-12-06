library(dplyr)
library(tidyr)

t <- read.csv("Q10-input-titanic.csv")
o = filter(t, Survived == 0) %>% group_by(Pclass) %>% summarise(n = n())
o 
#write.csv(o, file="Q10-output-titanic.csv", row.names = FALSE, quote=FALSE)
