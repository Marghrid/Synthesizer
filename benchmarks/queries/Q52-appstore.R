library(dplyr)
library(tidyr)
library(lubridate)

df <- read.csv(file = "./Q52-appstore.csv", header = TRUE, sep = ",")
out <- df %>% group_by(Content.Rating) %>% filter(!is.nan(Rating)) %>% summarize(mean=mean(Rating))
out %>% write.csv(file="./Q52-appstore_out.csv", row.names = FALSE, quote=FALSE)


