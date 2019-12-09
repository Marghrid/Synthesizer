first <- unname(unlist(sapply(df[1,], as.character)))

dateFormats = c("%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%Y-%m-%d", "%m/%d/%Y")

isDate <- function(x) 
            !(is.na(as.Date(as.character(x),
                            format=dateFormats)))

isDate(first[1])
isDate(first[2])