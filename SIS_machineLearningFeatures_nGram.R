# Title: Sure Independent Sampling for Predictor Selection
# Author: Nick Kurtansky
# Project: Selecting features for a Machine Learning algorithm
#
# 8/26/2019 nGram


library(MASS)
library(dplyr)

# load data
csv <- read.csv("Feature Generating Data\\SIS\\SIS_3nGramKeywords_20190826.csv", header=TRUE)
id.column_no <- which(colnames(csv) == 'Accession.No')
Accession.No <- csv[ ,id.column_no]
csv <- csv %>% select(-c(1, id.column_no))
# accession number column at index 1
csv <- cbind(Accession.No, csv)

# outcome and predictor matrices
Y <- csv %>% select(301:302)
X <- csv %>% select(2:300)

# Step 1: Initialize beta matrix
B <- matrix(NA, nrow = ncol(X), ncol = length(unique(Y[,1])) + 1)
colnames(B) <- c("predictor", as.character(sort(unique(Y$mpath_dx))))
B[,1] <- colnames(X)
# initialize the ranked beta matrix
Rank <- B

# Step 2: perform SIS for each diagnosis group
for(dx in 2:length(colnames(B))){
  for(p in 1:nrow(B)){
    print(paste(colnames(B)[dx], p / nrow(B)))
    Y_dx <- ifelse(Y$codedDxRegex == dx, 1, 0)
    B[p,dx + 1] <- abs(glm(Y_dx~X[,p], family="binomial")$coefficients[2])
  }
}


# Step 3: rank the betas
for(dx in 2:ncol(Rank)){
  print(colnames(Rank)[dx])
  ranks <- (abs(nrow(Rank)+1-rank(B[,dx])))
  Rank[,dx] <- ranks
}
#Rank

# Step 3: Arbitrary top 50
write.csv(x = Rank, file = "Feature Generating Data\\SIS\\rankedBeta_3nGram_20190826.csv", row.names = FALSE)

# Step 4: Arrive at top 30
#   Cut it down to 50 using score = 1/3*1/min + 1/3*1/average + 1/3*1/median
#   Cut it down to 30 using advice from Ofer

# Step 5: Produce matrix for Kivanc
#   [n = 30,000 * (30 keys + 8 dx)]
theList <- read.csv("Feature Generating Data\\SIS\\KeyNGrams.csv", header = T)
top150 <- X[,colnames(X) %in% theList[,1]]
top150 <- cbind(csv$Accession.No, top150)
colnames(top150)[1] <- "Accession.No"
Y_col <- csv[,c("Accession.No", "codedDxRegex")]

# load 30 keyord data
csv30 <- read.csv("Feature Generating Data\\SIS\\SIS_20190821.csv", header=TRUE)
X_30 <- csv30 %>% select(3:162)
oferList <- read.csv("Feature Generating Data\\SIS\\theOferList.csv", header = T)
top30 <- X_30[,colnames(X_30) %in% oferList$Ofer]
top30 <- cbind(csv30$Accession.No, top30)
colnames(top30)[1] <- "Accession.No"

KivancFile <- full_join(top30, top150, by = 'Accession.No')
KivancFile <- full_join(KivancFile, Y_col, by = 'Accession.No')
KivancFile <- KivancFile[,2:ncol(KivancFile)]
write.csv(x = KivancFile, file = "Feature Generating Data\\SIS\\Kivanc\\feature3nGram_20190826.csv", row.names = F)