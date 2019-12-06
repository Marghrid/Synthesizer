library(dplyr)
library(tidyr)
library(lubridate)

df <- read.csv(file = "./Q42-employee.csv", header = TRUE, sep = ",")

out <- df %>% group_by(Education) %>% summarize(n=n())

out %>% write.csv(file="./Q42-employee_out.csv", row.names = FALSE, quote=FALSE)