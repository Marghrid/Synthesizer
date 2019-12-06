library(dplyr)
library(tidyr)
library(lubridate)

df <- read.csv(file = "./Q45-members.csv", header = TRUE, sep = ",")

out <- df %>% mutate(wday=wday(registration_init_time)) %>% group_by(wday) %>% summarize(n=n())

out %>% write.csv(file="./Q45-members_out.csv", row.names = FALSE, quote=FALSE)