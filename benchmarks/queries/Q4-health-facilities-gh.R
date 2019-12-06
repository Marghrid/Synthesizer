library(dplyr)

out <- data %>% group_by(Region) %>% summarize(count=n()) %>% arrange(desc(count))

