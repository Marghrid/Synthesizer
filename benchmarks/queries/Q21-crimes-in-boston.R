library(dplyr)
library(tidyr)


data <-  read.csv(file = "./Q21-crimes-in-boston.csv", header = TRUE, sep = ",")
data %>% group_by(OFFENSE_CODE_GROUP) %>% summarize(n=n()) %>% top_n(10, n) %>% arrange(desc(n))
# data %>% write.csv(file="./Q21-airline-sentiment_out.csv", row.names = FALSE, quote=FALSE)