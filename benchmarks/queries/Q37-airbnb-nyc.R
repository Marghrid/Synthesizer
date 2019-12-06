library(dplyr)
library(tidyr)

data <- read.csv(file = "./Q37-airbnb-nyc.csv", header = TRUE, sep = ",")
out <- data %>% group_by(neighbourhood_group) %>% summarize(median = median(price))
out %>% write.csv(file="./Q37-airbnb-nyc_out.csv", row.names = FALSE, quote=FALSE)


