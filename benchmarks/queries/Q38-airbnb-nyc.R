library(dplyr)
library(tidyr)

data <- read.csv(file = "./Q38-airbnb-nyc.csv", header = TRUE, sep = ",")
out <- data %>% group_by(section_of_number_of_reviews) %>% summarize(median = median(price))
out %>% write.csv(file="./Q38-airbnb-nyc_out.csv", row.names = FALSE, quote=FALSE)


