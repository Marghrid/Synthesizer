library(dplyr)
library(tidyr)

t <- read.csv(file="Q8-input-avocado.csv", header=TRUE, sep=",")
o <- filter(t, year == 2016) %>% select(Small.Bags, Large.Bags, XLarge.Bags) %>% gather(Bags, Number) %>% group_by(Bags) %>% summarise(n = sum(Number))
o
#write.csv(o, file="Q8-output-avocado.csv", row.names = FALSE, quote=FALSE)

