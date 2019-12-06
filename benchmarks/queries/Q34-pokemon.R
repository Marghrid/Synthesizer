library(dplyr)
library(tidyr)

t <- read.csv("Q34-input-pokemon.csv")
o =  group_by(t, Type.1) %>% summarize(n = n()) %>% arrange(desc(n)) %>% top_n(5)
o 
#write.csv(o, file="Q34-output-pokemon.csv", row.names = FALSE, quote=FALSE)
