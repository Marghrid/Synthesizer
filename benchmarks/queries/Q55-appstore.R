library(dplyr)
library(tidyr)
library(lubridate)

df <- read.csv(file = "./Q55-appstore.csv", header = TRUE, sep = ",")
out <- df %>% group_by(Type) %>% filter(!is.nan(Rating)) %>% summarize(mean=mean(Rating))
out %>% write.csv(file="./Q55-appstore_out.csv", row.names = FALSE, quote=FALSE)


