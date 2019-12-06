library(dplyr)
library(tidyr)

df <- read.csv(file = "./Q40-gun-violence.csv", header = TRUE, sep = ",")

out <- df %>% group_by(state) %>% summarize(n = sum(victims)/n()) %>% arrange(desc(n)) %>% filter(n>0.8)

out %>% write.csv(file="./Q40-gun-violence_out.csv", row.names = FALSE, quote=FALSE)



