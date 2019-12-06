library(dplyr)
library(tidyr)


data <- read.csv("./Q22-immigrants_by_nationality.csv")
immigrants <- data %>% filter(Year == 2017, Nationality != "Spain") %>% 
					   group_by(Nationality) %>% summarize(n=sum(Number)) %>% 
					   top_n(10, n) %>% arrange(desc(n))

write.csv(immigrants, './Q22-immigrants_by_nationality_out.csv', row.names = FALSE, quote=FALSE)