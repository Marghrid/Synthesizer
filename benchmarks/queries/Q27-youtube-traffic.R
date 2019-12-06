library(dplyr)

data <- read.csv("./Q27-youtube-traffic.csv")
out <- data %>% group_by(category_id) %>% summarize(x=n()) %>% arrange(desc(x))%>% top_n(10,x)
out %>% write.csv("./Q27-youtube-traffic_out.csv", row.names = FALSE, quote=FALSE)