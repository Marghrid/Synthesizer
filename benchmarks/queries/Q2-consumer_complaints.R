library(dplyr)
library(tidyr)

x <- read.csv(file = "./consumer_complaints.csv", header = TRUE, sep = ",")
x <- x %>% group_by(company) %>%
      summarise(count = n()) %>%
      top_n(n=10, wt=count) 
      