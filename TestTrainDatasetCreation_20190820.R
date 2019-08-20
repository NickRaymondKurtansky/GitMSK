# Title: Training/Test Dataset Creation
# Author: Nick Kurtansky
#
# 8/20/2019
# Create an n report size data set balanced by year 
# and proportional to regex dx group proportion

library(dplyr)
rm(list=ls())
dxproportion = 'balanced'
yearproportion = 'balanced'
sample_size = 400

# get your data
format_data <- function(filename = 'MPATHclass_20190820.csv'){
  data <- read.csv(filename, header = T, stringsAsFactors = F)
  data$mpath_dx <- factor(data$mpath_dx)
  data$ReportDate <- as.Date(format(data$ReportDate), '%Y-%m-%d')
  data$Year <- as.numeric(format(data$ReportDate, '%Y'))
  return(data)
}

# outputs a uniform pdf
pdf_balanced <- function(data = data, variable){
  x_var <- unique(data[,variable])
  p_var <- rep(1 / length(x_var), times = length(x_var))
  pdf_var <- data.frame(x_var, p_var)
  return(pdf_var)
}

# outputs a relative requency pdf
pdf_weighted <- function(data = data, variable){
  rel.freq <- data %>% group_by(data[,variable]) %>% summarise(n = n()) %>% mutate(rel.freq = n / sum(n))
  pdf_var <- data.frame(rel.freq[,1], rel.freq$rel.freq)
  colnames(pdf_var) <- c('x_var', 'p_var')
  return(pdf_var)
}


main <- function(filename, sample_size, yearproportion = 'balanced', dxproportion = 'weighted', csvname = 'trainingset_20190820.csv'){
  # READ DATA
  # SINCE MOST DX ARE NON-MELANOCYTIC, LET'S VIEW THE DISTRIBUTIONS WITHOUT THEM,
  # AND THEN BACKTRACK TO TAKE AN UNDERREPRESENTATIVE SAMPLE OF THEM.
  data_full <- format_data()
  data <- data_full %>% filter(mpath_dx != 'Non-melanocytic lesion')
  
  # CREATE YEAR PDF
  if(yearproportion == 'balanced'){
    # create balanced pdf_years
    pdf_years <- pdf_balanced(data = data_full, variable = 'Year')
    } else if(yearproportion == 'weighted'){
    # created wefihted pdf_years
    pdf_years <- pdf_weighted(data = data_full, variable = 'Year')
  } else{
    return(print('entered unsupported year distribution method'))
  }
  
  # CREATE DX PDF
  if(dxproportion == 'balanced'){
    # create balanceed pdf_dx
    pdf_dx <- pdf_balanced(data_full, 'mpath_dx')
  } else if(dxproportion == 'weighted'){
    # create weighted pdf_dx
    pdf_dx <- pdf_weighted(data, 'mpath_dx')
    # SINCE MOST ARE MELANOCYTIC IN DATASET, LET'S UNDERESTIMATE THEIR PROPORTION
    nonmelanocytic <- data.frame(c('Non-melanocytic lesion'), c(sum(pdf_dx$p_var *(1/8))))
    colnames(nonmelanocytic) <- c("x_var", "p_var")
    pdf_dx$p_var <- pdf_dx$p_var * (7/8)
    pdf_dx <- rbind(pdf_dx, nonmelanocytic)
  } else{
    return(print('entered unsupported diagnoses distribution method'))
  }
  
  # sample the dataset using the pdfs create previously
  out.frame <- data[FALSE,]
  i = 1
  while(nrow(out.frame) < sample_size){
    i_year <- toString(sample(x = pdf_years$x_var, size = 1, prob = pdf_years$p_var))
    i_dx <- toString(sample(x = pdf_dx$x_var, size = 1, prob = pdf_dx$p_var))
    i_data <- data_full %>% filter(Year == i_year & mpath_dx == i_dx)
    # if no such cases, next
    if(length(i_data$X) == 0){
      next
    }
    i_id <- sample(i_data$X, size = 1)
    if(i_id %in% out.frame$X){
      next
    }
    out.frame <- rbind(out.frame, data_full[data_full$X == i_id,])
    print(i)
    i = i + 1
  }
  
  # write dataset as csv
  write.csv(x = out.frame, file = csvname, row.names = F)
}


main(sample_size = 400, yearproportion = 'balanced', dxproportion = 'balanced', csvname = 'balanced_trainingset_20190820.csv')