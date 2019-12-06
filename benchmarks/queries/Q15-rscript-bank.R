library(dplyr)
library(tidyr)

t <- read.csv("Q15-input-bank.csv")
o = filter(t, Exited == 1) %>% group_by(Gender) %>% summarise(n = n())
o 
#write.csv(o, file="Q15-output-bank.csv", row.names = FALSE, quote=FALSE)
