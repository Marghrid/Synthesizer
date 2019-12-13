tmp <- sample_n(df,10)
first <- unname(unlist(sapply(tmp, as.character)))

dateFormats = c("%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y")
lubriFormat = c("dmy", "dmy", "ymd", "ymd", "mdy", "mdy")

isDate <- function(x)
            !(is.na(as.Date(as.character(x),
                            format=dateFormats, tz = "UTC")))

out <- c()
formats <- list()
for (i in 1:length(tmp)) {
    out_tmp = c(TRUE, TRUE, TRUE, TRUE, TRUE, TRUE)
    for (j in 1:10) {
        truth_value <- isDate(first[j,i])
        out_tmp <- out_tmp & truth_value
    }
    if (!all(!out_tmp)) {
        out <- append(out, i)
        formats[[i]] <- c(lubriFormat[out_tmp])
    }
}

