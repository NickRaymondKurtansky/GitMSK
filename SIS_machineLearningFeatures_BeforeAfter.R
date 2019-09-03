# Title: Sure Independent Sampling for Predictor Selection
# Author: Nick Kurtansky
# Project: Selecting features for a Machine Learning algorithm
#
# 8/21/2019 Keyword Features
# 8/22/2019 Words Nearby Keyword Features


rm(list=ls())

library(MASS)
library(dplyr)

# load data
# list of keywords
Top30 <- read.csv("Feature Generating Data\\SIS\\theOferList.csv", header=TRUE)
keyword <- Top30$Ofer
# per lesion data
csv <- read.csv("Feature Generating Data\\SIS\\SIS_BeforeAfter30Keywords_20190823.csv", header=TRUE)
# diagnoses list
diagnoses <- sort(unique(csv$mpath_dx))
# feature columns
data <- csv[,3:434]
# outcome column
RegexDx <- data$codedDxRegex

# initialize beta matrix
B <- matrix(NA, nrow = ncol(data) - 1 - length(keyword), ncol = length(diagnoses) + 1)
index = 1

# Step 1: perform indepenedent simple log regressions
# keyword must be present
birthdaycake <- data
for(key in keyword){
  print(paste(key, "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"))
  col_bank <- c()
  for(i in 1:ncol(birthdaycake)){
    if(toString(key) == strsplit(colnames(birthdaycake)[i], "_")[[1]][1]){
      col_bank <- c(col_bank, i)
    }
  }
  slice <- cbind(birthdaycake[,col_bank], RegexDx)
  birthdaycake <- birthdaycake[,-col_bank]
  # keyword must = 1
  slice <- slice[slice[1] == 1,]
#  slice <- slice[,-1]
  for(p in 2:(ncol(slice) - 1)){
    for(d in 1:length(diagnoses)){
      print(paste(diagnoses[d], p, sep = "_"))
      predictor <- colnames(slice)[p]
      X_slice <- slice[,p]
      Y_slice <- slice %>% mutate(Y = ifelse(RegexDx == d, 1, 0))
      B[index, 1] <- predictor
      B[index, d + 1] <- abs(glm(Y_slice$Y~X_slice, family="binomial")$coefficients[2])
    }
    index = index + 1
  }
}


# Step 2: Rank the independent coefficients
p <- nrow(B)
coef1 <- rep(NA, p)
coef2 <- rep(NA, p)
coef3 <- rep(NA, p)
coef4 <- rep(NA, p)
coef5 <- rep(NA, p)
coef6 <- rep(NA, p)
coef7 <- rep(NA, p)
coef8 <- rep(NA, p)
id <- B[,1]
Rank <- data.frame(id, coef1, coef2, coef3, coef4, coef5, coef6, coef7, coef8)
for(dx in 1:length(diagnoses)){
  print(diagnoses[dx])
  ranks <- (abs(nrow(B)+1-rank(B[,dx+1])))
  Rank[,dx+1] <- ranks
}
Rank


# Step 3: Arbitrary top 50
write.csv(x = Rank, file = "Feature Generating Data\\SIS\\rankedBeta_beforeAfter30Keywords_20190823.csv", row.names = FALSE)


# Step 4: Arrive at top 30
#   Cut it down to 50 using score = 1/3*1/min + 1/3*1/average + 1/3*1/median
#   Cut it down to 30 using advice from Ofer


# # Step 5: Produce matrix for Kivanc
# #   [n = 30,000 * (30 keys + 8 dx)]
# theList <- read.csv("Feature Generating Data\\SIS\\theOferList.csv", header = T)
# top30 <- X[,colnames(X) %in% theList$Ofer]
# KivancFile <- cbind(top30, Y)
# write.csv(x = KivancFile, file = "Feature Generating Data\\SIS\\Kivanc\\featureSingleKeyword_20190821.csv", row.names = F)