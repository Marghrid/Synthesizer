library(dplyr)
library(tidyr)

df <- read.csv(file = "./Q47-members.csv", header = TRUE, sep = ",")

out <- df %>% group_by(gender) %>% summarize(n=n())

out %>% write.csv(file="./Q47-members_out.csv", row.names = FALSE, quote=FALSE)