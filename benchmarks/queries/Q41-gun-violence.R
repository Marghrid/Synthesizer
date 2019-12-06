library(dplyr)
library(tidyr)
library(lubridate)

df <- read.csv(file = "~/Downloads/Q41-gun-violence.csv", header = TRUE, sep = ",")

out <- df %>% mutate(weekday=wday(date)) %>% group_by(weekday) %>% summarize(n=n())

out %>% write.csv(file="~/Downloads/Q41-gun-violence_out.csv", row.names = FALSE, quote=FALSE)



