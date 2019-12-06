library(dplyr)
library(tidyr)

df <- read.csv(file = "./Q49-videogame.csv", header = TRUE, sep = ",")

out <- df %>% group_by(Work.Rate) %>% summarize(n=n()) 

out %>% write.csv(file="./Q49-videogame_out.csv", row.names = FALSE, quote=FALSE)