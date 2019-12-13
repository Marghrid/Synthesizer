library(dplyr)
library(tidyr)

t <- read.csv("./Q28-youtube-traffic.csv")

t <- mutate(time_between = trending_date - publish_time) %>%
     group_by(time_between) %>%
     summarize(Sum=n()) %>%
     arrange(time_between) %>%
     head(10)


t %>% write.csv(file="./Q28-youtube-traffic_out.csv", row.names = FALSE, quote=FALSE)
