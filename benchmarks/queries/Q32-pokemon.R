library(dplyr)
library(tidyr)

t <- read.csv("Q32-input-pokemon.csv")
o =  filter(t, Generation == 3) %>% group_by(Generation) %>% summarise(attack = mean(Attack), defense = mean(Defense)) %>% select(-Generation) %>% gather(Stats, Value)
o 
#write.csv(o, file="Q32-output-pokemon.csv", row.names = FALSE, quote=FALSE)
