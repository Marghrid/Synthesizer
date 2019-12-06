library(dplyr)
library(tidyr)

x <- read.csv(file = "./consumer_complaints.csv", header = TRUE, sep = ",")

year_compaints_dplyr <- x %>% mutate(date_received = mdy(date_received)) %>%
						mutate(year = year(date_received)) %>%
                    	group_by(year) %>%
                    	summarise(count = n())