library(dplyr)
library(tidyr)

t <- read.csv("Q18-input-work.csv")
o = group_by(t, sales, left) %>% summarise(n = n()) %>% spread(left, n) %>% mutate(ratio = `1` / (`1`+`0`)) %>% select(sales, ratio)
o 
#write.csv(o, file="Q18-output-work.csv", row.names = FALSE, quote=FALSE)
