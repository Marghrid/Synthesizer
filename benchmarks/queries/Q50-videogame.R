library(dplyr)
library(tidyr)

df <- read.csv(file = "./Q50-videogame.csv", header = TRUE, sep = ",")

out <- df %>% group_by(Nationality) %>% summarize(n=mean(Overall)) %>% top_n(10, n) %>% arrange(desc(n))

out %>% write.csv(file="./Q50-videogame_out.csv", row.names = FALSE, quote=FALSE)