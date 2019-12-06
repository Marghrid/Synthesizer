library(dplyr)
library(tidyr)

t <- read.csv("Q16-input-bank.csv")
o = group_by(t, Geography, Exited) %>% summarise(n = n()) %>% unite(Name, Geography, Exited)
o 
write.csv(o, file="Q16-output-bank.csv", row.names = FALSE, quote=FALSE)
