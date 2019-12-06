library(dplyr)
library(tidyr)

t <- read.csv("Q30-input-wine.csv")
o = drop_na(t) %>% select(-X) %>% gather(Wine, Score) %>% group_by(Wine) %>% summarise(Score = mean(Score))
o 
#write.csv(o, file="Q30-output-wine.csv", row.names = FALSE, quote=FALSE)
