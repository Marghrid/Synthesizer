library(dplyr)
library(tidyr)

data <- read.csv(file = "./Q36-airbnb-nyc.csv", header = TRUE, sep = ",")
out <- data %>% group_by(room_type) %>% summarize(n=n()) %>% mutate(n=n/sum(n))
out %>% write.csv(file="./Q36-airbnb-nyc_out.csv", row.names = FALSE, quote=FALSE)