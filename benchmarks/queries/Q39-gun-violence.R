library(dplyr)
library(tidyr)
library(lubridate)

df <- read.csv(file = "./Q39-gun-violence.csv", header = TRUE, sep = ",")

out <- df %>% mutate(year=year(date)) %>% group_by(year) %>% summarize(n=n())

out %>% write.csv(file="./Q39-gun-violence_out.csv", row.names = FALSE, quote=FALSE)