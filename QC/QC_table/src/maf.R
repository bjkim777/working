#!/usr/bin/env Rscript

args = commandArgs(trailingOnly=TRUE)

if (length(args) < 3) {
    stop("maf.R [input file] [main text] [output file]", call.=FALSE)
}

png(args[3])
df = read.table(args[1], header=FALSE)
max_depth = max(df$V1)
depth_len = length(df$V1)
plot(df$V2, axes=F, type="l", xlab="Depth", ylab="Cumulative variants allele frequency", main=args[2])
axis(1, at=1:depth_len, lab=df$V1)
axis(2, las=1, at=0.2*0:5)
lines(df$V3, type="l", col="blue")
lines(df$V4, type="l", col="red")
legend(depth_len - 3, 0.6, c("MAF < 0.05", "MAF 0.05 - 0.1", "MAF > 0.1"), cex=0.8, col=c("black", "blue", "red"), lty=c(1,1,1))
dev.off()
