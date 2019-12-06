library(dplyr)
library(tidyr)

t <- read.csv("Q19-input-work.csv")
o = group_by(t, salary, left) %>% summarise(n = n()) %>% unite(Name, salary, left)
o 
#write.csv(o, file="Q19-output-work.csv", row.names = FALSE, quote=FALSE)
