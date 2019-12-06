library(dplyr)
library(tidyr)

t <- read.csv(file="/home/drr/flight_delays.csv", header=TRUE, sep=",")
t <- t %>% gather("company", "scores", -1) %>% filter(company == "NK") %>% select("Month", "scores")
t %>% write.csv(file="/home/drr/flight_delays_out.csv", row.names = FALSE, quote=FALSE)