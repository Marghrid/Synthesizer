library(dplyr)
library(tidyr)
library(lubridate)

df <- read.csv(file = "./Q51-aircraft.csv", header = TRUE, sep = ",")

out <- df %>% group_by(equipment) %>% summarize(n=n()) %>% mutate(n=n/sum(n)*100) %>% top_n(10,n) %>% arrange(desc(n))

out %>% write.csv(file="./Q51-aircraft_out.csv", row.names = FALSE, quote=FALSE)