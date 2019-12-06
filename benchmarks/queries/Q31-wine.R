library(dplyr)
library(tidyr)

t <- read.csv("Q31-input-wine.csv")
o = drop_na(t) %>% select(-X) %>% gather(Wine, Score) %>% group_by(Wine) %>% filter(Score > 90 ) %>% summarise(Score = n ()) 
o 
#write.csv(o, file="Q31-output-wine.csv", row.names = FALSE, quote=FALSE)
