library(dplyr)
library(tidyr)

data <- read.csv(file = "./Q35-airbnb-nyc.csv", header = TRUE, sep = ",")
out <- data %>% group_by(neighbourhood_group) %>% summarize(n=n()) %>% mutate(n=n/sum(n))
out %>% write.csv(file="./Q35-airbnb-nyc_out.csv", row.names = FALSE, quote=FALSE)