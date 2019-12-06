library(dplyr)
library(tidyr)


deaths <- read.csv("./Q23-deaths-barcelona.csv")
deaths %>% filter(Year!="2017") %>%
           group_by(Age) %>%
           summarise(Count=sum(Number))
