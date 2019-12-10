first <- unname(unlist(sapply(df[1,], as.character)))

dateFormats = c("%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y")
lubriFormat = c("dmy", "dmy", "ymd", "ymd", "mdy", "mdy")

isDate <- function(x) 
            !(is.na(as.Date(as.character(x),
                            format=dateFormats, tz = "UTC")))


out <- c()
formats <- list()
for (i in 1:length(first)) {
    truth_value <- isDate(first[i])
    if (!all(!truth_value)) {
        out <- append(out, i)
        formats[[i]] <- c(lubriFormat[truth_value])
    }
}

out
formats