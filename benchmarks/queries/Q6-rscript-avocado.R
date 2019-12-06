library(dplyr)
library(tidyr)

t <- read.csv(file="Q6-input-avocado.csv", header=TRUE, sep=",")
group_by(t, year) %>% summarise(mean = mean(AveragePrice))
