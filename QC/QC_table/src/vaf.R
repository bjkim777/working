#!/usr/bin/env Rscript

args = commandArgs(trailingOnly=TRUE)

if (length(args) < 3) {
    stop("vaf.R [input file] [main text] [output file]", call.=FALSE)
}

png(args[3])
df = read.table(args[1], header=FALSE)
df_mat = matrix(df$V2, nrow=1)
colnames(df_mat) = df$V1
barplot(df_mat, xlab="Variants allele frequency (%)", ylab="Average number of variants", main=args[2])
dev.off()
