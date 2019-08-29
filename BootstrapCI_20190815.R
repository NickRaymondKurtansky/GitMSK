#### BOOTSTRAP CONFIDENCE INTERVALS
#### Nick Kurtansky
####
#### 8/14/2019
#### Mean
#### Correlation
#### Balanced multi-class accuracy
####
#### 8/15/2019
#### Adding a smoothed bootstrap option
#### Odds Ratio
#### Sample Standard Dev
####
#### 8/27/2019
#### Median

library(dplyr)

# Smoothed bootstrap utility
smoothed_boot <- function(v, switch = "no"){
  n <- nrow(v)
  if(switch == "no"){
    return(sample_n(v, size = n, replace = TRUE))
  }
  else{
    # conventional choice for small amount of random noise N(0,1/sqrt(n))
    sigma <- 1 / sqrt(n)
    theta <- 0
    # add noise to each bootstrap sample
    v.star <- sample_n(v, size = n, replace = TRUE)
    noise <- rnorm(n, mean = theta, sd = sigma)
    return(v.star + noise)
  }
}


# Mean
boot_mean <- function(v, B = 10000, smoothed = "no"){
  # maximum likelihood estimation of population mean
  thetahat <- mean(v, na.rm = T)
  B.thetahat <- rep(NA, times = B)
  v <- data.frame(v)
  for(b in 1:B){
    v.star <- smoothed_boot(v, switch = smoothed)[,1]
    thetahat.star <- mean(v.star)
    B.thetahat[b] <- thetahat.star
  }
  B.thetahat <- sort(B.thetahat)
  boot.se <- sd(B.thetahat)
  out1 <- thetahat
  # normal method
  out2 <- round(c(thetahat - 1.96*boot.se, thetahat + 1.96*boot.se), 2)
  # percentile method
  out3 <- round(B.thetahat[c(length(B.thetahat)*.025, length(B.thetahat)*.975)], 2)
  out <- list(out1, out2, out3)
  names(out) <- c("mean", "normal", "percentile")
  return(out)
}


# CORRELATION
boot_cor <- function(v1, v2, B = 10000, smoothed = "no"){
  # maximum likelihood estimation of pearsons correlation
  rhat <- cor(v1, v2, method = "pearson")
  B.rhat <- rep(NA, times = B)
  for(b in 1:B){
    sample.star <- smoothed_boot(data.frame(v1,v2), switch = smoothed)
    rhat.star <- cor(sample.star[,1], sample.star[,2], method = "pearson")
    B.rhat[b] <- rhat.star
  }
  B.rhat <- sort(B.rhat)
  se.B.rhat <- sd(B.rhat)
  out1 <- rhat
  # normal method
  out2 <- round(c(rhat - 1.96*se.B.rhat, rhat + 1.96*se.B.rhat), 2)
  # percentile method
  out3 <- round(B.rhat[c(length(B.rhat)*.025, length(B.rhat)*.975)], 2)
  out <- list(out1, out2, out3)
  names(out) <- c("correlation", "normal", "percentile")
  return(out)
}


# BALANCED CLASS ACCURACY
boot_BCA <- function(lizt, B = 10000, smoothed = "no"){
  # maximum likelihood estimation of BCA
  phat <- rep(NA, times = length(lizt))
  for(i in 1:length(lizt)){
    phat[i] <- mean(lizt[[i]])
  }
  BCA.hat <- mean(phat)
  # bootstrap time
  B.BCA.hat <- rep(NA, times = B)
  for(j in 1:B){
    phat.star <- rep(NA, times = length(lizt))
    for(i in 1:length(lizt)){
      ij.star <- smoothed_boot(data.frame(lizt[[i]]), switch = smoothed)[,1]
      ij.phat.star <- mean(ij.star)
      phat.star[i] <- ij.phat.star
    }
    BCA.hat.star <- mean(phat.star)
    B.BCA.hat[j] <- BCA.hat.star
  }
  B.BCA.hat <- sort(B.BCA.hat)
  se.BCA.hat <- sd(B.BCA.hat)
  out1 <- BCA.hat
  # normal method
  out2 <- round(c(BCA.hat - 1.96*se.BCA.hat, BCA.hat + 1.96*se.BCA.hat), 2)
  # percentile method
  out3 <- round(B.BCA.hat[c(length(B.BCA.hat)*.025, length(B.BCA.hat)*.975)], 2)
  out <- list(out1, out2, out3)
  names(out) <- c("bca", "normal", "percentile")
  return(out)
}


# Odds Ratio
boot_OR <- function(frame, B = 10000, smoothed = "no"){
  frame <- data.frame(factor(frame[,1], levels <- c(1,0)), factor(frame[,2], levels <- c(1,0)))
  # maximum likelihood estimate for odds ratio
  confusion.hat <- table(frame[,1], frame[,2])
  # Haldane-Anscombe correction if any cell is 0
  while(min(confusion.hat) == 0){
    confusion.hat[which(as.vector(confusion.hat) == min(confusion.hat))] <- .5
  }
  orhat <- (confusion.hat[1,1]/confusion.hat[1,2]) / (confusion.hat[2,1]/confusion.hat[2,2])
  B.orhat <- rep(NA, times = B)
  for(b in 1:B){
    frame.star <- smoothed_boot(frame, switch = smoothed)
    confusion.star <- table(frame.star[,1], frame.star[,2])
    # Haldane-Anscombe correction if any cell is 0
    while(min(confusion.star) == 0){
      confusion.star[which(as.vector(confusion.star) == min(confusion.star))] <- .5
    }
    or.hat.star <- (confusion.star[1,1]/confusion.star[1,2]) / (confusion.star[2,1]/confusion.star[2,2])
    B.orhat[b] <- or.hat.star
  }
  B.orhat <- sort(B.orhat)
  # percentile method
  out1 <- orhat
  out2 <- round(B.orhat[c(length(B.orhat)*.025, length(B.orhat)*.975)], 2)
  out <- list(out1, out2)
  names(out) <- c("odds ratio", "percentile")
  return(out)
}


# Sample Standard Deviation
boot_VAR <- function(v, B = 10000){
  # maximum likelihood estimation of sample standard deviation
  sdhat <- sd(v)
  B.sdhat <- rep(NA, times = B)
  v <- data.frame(v)
  for(b in 1:B){
    v.star <- smoothed_boot(v, switch = "no")[,1]
    sdhat.star <- sd(v.star)
    B.sdhat[b] <- sdhat.star
  }
  B.sdhat <- sort(B.sdhat)
  boot.se <- sd(B.sdhat)
  out1 <- sdhat
  # normal method
  out2 <- round(c(sdhat - 1.96*boot.se, sdhat + 1.96*boot.se), 2)
  # percentile method
  out3 <- round(B.sdhat[c(length(B.sdhat)*.025, length(B.sdhat)*.975)], 2)
  out <- list(out1, out2, out3)
  names(out) <- c("sample sd", "normal", "percentile")
  return(out)
}


# Median
boot_median <- function(v, B = 10000, smoothed = "no"){
  # maximum likelihood estimation of population mean
  thetahat <- median(v)
  B.thetahat <- rep(NA, times = B)
  v <- data.frame(v)
  for(b in 1:B){
    v.star <- smoothed_boot(v, switch = smoothed)[,1]
    thetahat.star <- median(v.star)
    B.thetahat[b] <- thetahat.star
  }
  B.thetahat <- sort(B.thetahat)
  boot.se <- sd(B.thetahat)
  out1 <- thetahat
  # normal method
  out2 <- round(c(thetahat - 1.96*boot.se, thetahat + 1.96*boot.se), 2)
  # percentile method
  out3 <- round(B.thetahat[c(length(B.thetahat)*.025, length(B.thetahat)*.975)], 2)
  out <- list(out1, out2, out3)
  names(out) <- c("median", "normal", "percentile")
  return(out)
}

