library(dplyr)
library(tidyr)
library(lubridate)

df <- read.csv(file = "./Q44-members.csv", header = TRUE, sep = ",")

out <- df %>% mutate(year=year(registration_init_time)) %>% group_by(year) %>% summarize(n=n())

out %>% write.csv(file="./Q44-members_out.csv", row.names = FALSE, quote=FALSE)