# Title: Sure Independent Sampling for Predictor Selection
# Author: Nick Kurtansky
# Project: Selecting features for a Machine Learning algorithm
#
# 8/21/2019


library(MASS)
library(dplyr)

# load data
csv <- read.csv("Feature Generating Data\\SIS\\SIS_20190821.csv", header=TRUE)
Y <- csv %>% select(163:170)
X <- csv %>% select(3:162)

DX <- ncol(Y)
p <- ncol(X)

# perform SIS for each diagnosis group
# Step 1: perform indepenedent simple log regressions
coef1 <- rep(NA, p)
coef2 <- rep(NA, p)
coef3 <- rep(NA, p)
coef4 <- rep(NA, p)
coef5 <- rep(NA, p)
coef6 <- rep(NA, p)
coef7 <- rep(NA, p)
coef8 <- rep(NA, p)
id <- colnames(X)
B <- data.frame(id, coef1, coef2, coef3, coef4, coef5, coef6, coef7, coef8)

diagnoses <- colnames(Y)
for(dx in 1:DX){
  print(diagnoses[dx])
  for(i in 1:p){
    print(i)
    B[i,dx + 1] <- abs(glm(Y[,dx]~X[,i], family="binomial")$coefficients[2])
  }
}

# Step 2: Rank the independent coefficients
coef1 <- rep(NA, p)
coef2 <- rep(NA, p)
coef3 <- rep(NA, p)
coef4 <- rep(NA, p)
coef5 <- rep(NA, p)
coef6 <- rep(NA, p)
coef7 <- rep(NA, p)
coef8 <- rep(NA, p)
id <- colnames(X)
Rank <- data.frame(id, coef1, coef2, coef3, coef4, coef5, coef6, coef7, coef8)
for(dx in 1:DX){
  print(colnames(Y)[dx])
  ranks <- (abs(p+1-rank(B[,dx+1])))
  Rank[,dx+1] <- ranks
}
Rank

# Step 3: Arbitrary top 50
write.csv(x = Rank, file = "Feature Generating Data\\SIS\\rankedBeta_20190821.csv", row.names = FALSE)

# Step 4: Arrive at top 30
#   Cut it down to 50 using score = 1/3*1/min + 1/3*1/average + 1/3*1/median
#   Cut it down to 30 using advice from Ofer

# Step 5: Produce matrix for Kivanc
#   [n = 30,000 * (30 keys + 8 dx)]
theList <- read.csv("Feature Generating Data\\SIS\\theOferList.csv", header = T)
top30 <- X[,colnames(X) %in% theList$Ofer]
KivancFile <- cbind(top30, Y)
write.csv(x = KivancFile, file = "Feature Generating Data\\SIS\\Kivanc\\featureSingleKeyword_20190821.csv", row.names = F)