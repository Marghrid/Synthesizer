library(dplyr)
library(tidyr)

t <- read.csv("Q17-input-work.csv")
o = t %>% group_by(left) %>% summarise( avg = mean(average_montly_hours))
o 
#write.csv(o, file="Q17-output-work.csv", row.names = FALSE, quote=FALSE)
