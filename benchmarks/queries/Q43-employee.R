library(dplyr)
library(tidyr)
library(lubridate)

df <- read.csv(file = "./Q43-employee.csv", header = TRUE, sep = ",")

out <- df %>% group_by(Gender) %>% summarize(n=sum(JobSatisfaction))

out %>% write.csv(file="./Q43-employee_out.csv", row.names = FALSE, quote=FALSE)

