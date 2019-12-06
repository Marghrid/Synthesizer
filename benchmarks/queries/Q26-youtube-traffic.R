library(dplyr)

data <- read.csv("./Q26-youtube-traffic.csv")
out <- data %>% group_by(channel_title) %>% summarize(Sum=n()) %>% arrange(desc(Sum)) %>% top_n(10, Sum)
out %>% write.csv("./Q26-youtube-traffic_out.csv", row.names = FALSE, quote=FALSE)