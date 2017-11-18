#!/usr/bin/env Rscript
suppressMessages(library(plotly))

# Usage
usage = "Usage\nRscript kmer_plot.r <path to bbmap khist.sh> <path to fastq> <output file> < (optional) existing kmer count table>"

# parse arguments
args <- commandArgs(TRUE)
path_to_khist = args[1]
fastq = args[2]
out_file = args[3]
count_table = args[4]

# test if required arguments are provided
if (length(args) < 2) {
  stop(usage)
} else if (is.na(out_file)) {
  out_file = "kmer_plot.html" # default output file name
}

# check if path to khist.sh is valid
if (!endsWith(path_to_khist, "khist.sh")){
  stop("Please provide valid path to khist.sh of bbmap")
}

# create kmer count table if none provided
if (is.na(count_table)) {
  count_table = 'khist_tmp.txt'
  system(paste0(path_to_khist, ' in=', fastq, ' hist=', count_table))
}

# load count table
count_table <- read.table(count_table, header = F)
colnames(count_table) <- c('depth', 'raw_count', 'unique_count')

# font style
f <- list(
  size = 18,
  color = "black")

# plot titles
title_left <- list(
  text = "Count of unique kmers",
  font = f,
  xref = "paper",
  yref = "paper",
  yanchor = "bottom",
  xanchor = "center",
  align = "center",
  x = 0.5,
  y = 1,
  showarrow = FALSE
)

title_right <- list(
  text = "Cumulative fraction of kmers",
  font = f,
  xref = "paper",
  yref = "paper",
  yanchor = "bottom",
  xanchor = "center",
  align = "center",
  x = 0.5,
  y = 1,
  showarrow = FALSE
)

# plot left panel
p1 <- plot_ly(count_table, x = ~depth, y = ~unique_count, type = 'scatter', mode = 'lines+markers', name = "Unique kmers") %>% layout(annotations = title_left, xaxis = list(title = "kmer frequency"), yaxis = list(title = "# unique kmers"))

# plot right panel
p2 <- plot_ly(count_table, x = ~depth, y = ~cumsum(unique_count)/sum(unique_count), type = 'scatter', mode = 'lines+markers', name = "Cumulative kmers") %>% layout(xaxis = list(type = "log", title = "kmer frequency"), yaxis = list(title = "cumulative fraction of kmers"), annotations = title_right)

# save plot
p <- subplot(p1, p2, titleX = T, titleY = F)
htmlwidgets::saveWidget(as_widget(p), out_file)
