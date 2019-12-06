library(dplyr)
library(tidyr)

data <- read.csv(file = "./Q29-youtube-traffic_out.csv", header = TRUE, sep = ",")

out <- data %>% group_by(bigram) %>% summarize(n=n()) %>% arrange(desc(n)) %>% top_n(10,n)

out %>% write.csv(file="./Q29-youtube-traffic_out.csv", row.names = FALSE, quote=FALSE)