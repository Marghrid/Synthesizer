library(dplyr)
library(tidyr)

data <- read.csv(file = "./Q14-airline-sentiment.csv", header = TRUE, sep = ",")

data %>% filter(negativereason != '') %>% group_by(negativereason) %>% summarize(n=n())

data %>% write.csv(file="./Q14-airline-sentiment_out.csv", row.names = FALSE, quote=FALSE)