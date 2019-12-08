library(dplyr)
library(tidyr)

data <- read.csv(file = "./Q38-airbnb-nyc.csv", header = TRUE, sep = ",")
out <- data %>% group_by(host_id) %>% summarize(n=n()) %>% top_n(10,n) %>% arrange(desc(n))
out %>% write.csv(file="./Q38-airbnb-nyc_out.csv", row.names = FALSE, quote=FALSE)


