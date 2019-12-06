library(dplyr)
library(tidyr)

df <- read.csv(file = "./Q46-members.csv", header = TRUE, sep = ",")

out <- df %>% group_by(registered_via) %>% summarize(n=n())

out %>% write.csv(file="./Q46-members_out.csv", row.names = FALSE, quote=FALSE)