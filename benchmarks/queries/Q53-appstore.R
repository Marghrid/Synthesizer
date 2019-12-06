library(dplyr)
library(tidyr)
library(lubridate)

df <- read.csv(file = "./Q53-appstore.csv", header = TRUE, sep = ",")
out <- df %>% group_by(Content.Rating) %>% summarize(n=n())
out %>% write.csv(file="./Q53-appstore_out.csv", row.names = FALSE, quote=FALSE)


