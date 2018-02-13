#!/usr/bin/env Rscript

args = commandArgs(trailingOnly=TRUE)

if (length(args) < 3) {
    stop("moving_average.R [input file] [main text] [output file]", call.=FALSE)
}

png(args[3])
df = read.table(args[1], header=FALSE)
max_depth = max(df$V1)
df_ver2 = rep(df$V1, df$V2)
mean_depth = round(mean(df_ver2),2)
iqr = round(IQR(df_ver2),2)
max_around_depth = max_depth -max_depth %% 100 
by_depth = max_around_depth / 4
mp = barplot(df$V2, main=paste(args[2], "( IQR = ",iqr,")"), ylab="Frequency", xlab=paste("depth ( avg =",mean_depth,")"))

axis(side=1, at=c(0, mp[seq(0, max_around_depth, by_depth)]), labels=seq(0, max_around_depth, by_depth))
dev.off()
