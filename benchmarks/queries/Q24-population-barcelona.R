library(dplyr)
library(tidyr)

data <-  read.csv(file = "./Q24-population-barcelona.csv", header = TRUE, sep = ",")
data <- data %>% group_by(Sexe) %>% summarise(count=sum(Nombre)) %>% mutate(count=round(100*count/sum(count),2))