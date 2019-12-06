library(dplyr)
library(tidyr)


order_products__train <- read.csv("./Q20-instacart.csv")
order_products__train %>%   group_by(reordered) %>% 
                            summarize(count = n()) %>% 
                            mutate(reordered = as.factor(reordered)) %>%
                            mutate(proportion = count/sum(count))



