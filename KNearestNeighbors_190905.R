# Title: K "Nearest Neighbors" Calculation
# Author: Nicholas Kurtansky
# Project: Selecting features for a Machine Learning algorithm
#
# 9/4/2019 First draft using the apply function (worked but very inneffient)
# 9/5/2019 Build around matrix operations for efficiency


rm(list=ls())
library(dplyr)


# returns a vector of differences of a single observation from each observation in a matrix
pointDistance <- function(point_0, point_matrix){
  # input error checking
  if(ncol(point_matrix) != length(point_0)){
    return("Point vector must be of same dimenstional space as the point matrix")
  }
  # calculate the distance from point of interest to points in matrix
  distance_matrix <- matrix(NA, nrow(point_matrix), 2)
  distance_matrix[,1] <- sqrt(rowSums((point_0 - point_matrix)^2))
  distance_matrix[,2] <- rank(distance_matrix[,1], ties.method = "random")
  return(distance_matrix)
}


# returns the k nearest neighbors to a single point
helloNeighbor <- function(k = 1, id_0, point_matrix, rank_col = ncol(point_matrix)){
  # toss out the i'th observation (it's the distance from itself)
  point_matrix <- point_matrix[-id_0,]
  point_matrix[,rank_col] <- rank(point_matrix[,rank_col], ties.method = "random")
  # return the k smallest differences
  return(point_matrix[which(point_matrix[,rank_col] <= k), ])
}


# calculate the proportion of dx != an inputted dx
diverseFeat <- function(featureId, featureVec){
  return(sum(featureVec != featureId) / length(featureVec))
}

#########################################################################################
#########################################################################################

timestamp <- "190905"

# read and format master dataframe
data <- read.csv("Feature Generating Data\\SIS\\Kivanc\\features_2D_20190829.csv", header = T)
masterFrame <- data[,c(1, 181, 182, 183)]
colnames(masterFrame) <- c("id", "dx", "x", "y")
#masterFrame$dx <- as.factor(masterFrame$dx)

# initiate proportional vector
closeNeighbor <- masterFrame
closeNeighbor$Diverse <- rep(NA, nrow(closeNeighbor))

# initiate feature matrix for efficiency
features <- as.matrix(masterFrame[,c(3:4)])

# INITIALIZED FOR EFFICIENCY
# matrix column: distance rank
rankc = 2
# matrix column: feature Id
featurec = 3

# loop through each for in the masterFrame
for(i in 1:nrow(features)){
  print(paste(i, "::", round(100*i / nrow(features), digits = 4), "%"))
  
  # initialize matix
  matrix_i <- matrix(NA, nrow(features), 3)
  
  # features for observation i
  p0 <- features[i,]
  dx0 <- masterFrame[i, 2]
  
  # similarity to observation i
  matrix_i[,c(1,2)] <- pointDistance(point_0 = p0, point_matrix = features)
  matrix_i[,3] <- as.numeric(masterFrame$dx)
  
  # 5 most similar observations
  iNear <- helloNeighbor(k = 5, id_0 = i, point_matrix = matrix_i, rank_col = rankc)
  # similarity score to i's 5 most similar observations 
  closeNeighbor$Diverse[i] <- diverseFeat(featureId = dx0, featureVec = iNear[,featurec])
}
write.csv(closeNeighbor, file = paste("Feature Generating Data\\SIS\\Kivanc\\DiverseNeighbors_", timestamp,".csv", sep = ""), row.names = FALSE)

