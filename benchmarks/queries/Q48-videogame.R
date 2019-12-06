library(dplyr)
library(tidyr)

df <- read.csv(file = "./Q48-videogame.csv", header = TRUE, sep = ",")

out <- df %>% group_by(Skill.Moves) %>% summarize(n=n()) %>% filter(!is.na(Skill.Moves))

out %>% write.csv(file="./Q48-videogame_out.csv", row.names = FALSE, quote=FALSE)