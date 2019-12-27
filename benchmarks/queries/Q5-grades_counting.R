library(dplyr)
library(tidyr)

t <- read.csv("../input_tables/grades.csv")
t <- summarise(group_by(filter(gather(t, Test, Grade, 2:9), Grade!='NA'), Test), m =n())
t %>% write.csv(file="../output_tables/grades_out.csv", row.names = FALSE, quote=FALSE)
