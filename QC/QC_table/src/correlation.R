#!/usr/bin/env Rscript

args = commandArgs(trailingOnly=TRUE)

if (length(args) < 5) {
    stop("correlation.R [input file] [X samples] [Y samples] [Main text] [output file]\n", call.=FALSE)
}

png(args[5])
df = read.table(args[1], header=FALSE)
cor_coe = cor(df$V2, df$V3)
plot(df$V2, df$V3, xlab=paste("Variants allele frequency of", args[2]), ylab=paste("Variants allele frequency of", args[3]), main=paste(args[4],"(",cor_coe,")"))
abline(lm(df$V3 ~ df$V2), col="blue")
dev.off()
