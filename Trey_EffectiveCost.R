library(ggplot2)
library(ggthemes)
library(scales)
library(dplyr)
library(tidyr)
library(extrafont)

# this is the data
data <- read.csv('Trey_EC_flatfile_190801.csv', header=T)
colnames(data)[1] <- c('treatment')

data_spread <- spread(data, key = 'variable', value = 'value')

# theme
style1 <- theme(panel.background = element_rect(fill = 'white'), panel.grid.major = element_blank(), axis.line = element_line(color = 'black'), text = element_text(size = 20, family = 'Arial'))
style2 <- theme(panel.background = element_rect(fill = 'white'), panel.grid.major = element_blank(), axis.line = element_line(color = 'black'), text = element_text(size = 20, family = 'Arial'), plot.title = element_text(hjust = .525))

# Adherence/Clearance vs. Treatment
ggplot(data_spread, aes(x = treatment)) +
  geom_col(aes(y = adherence, fill = 'Adherence'), position = position_nudge(x = +0.16), width = .32, color = 'black') +
  geom_col(aes(y = clearupperbound, fill = 'Upper Clearance est.'), position = position_nudge(x = -0.16), width = .32, color = 'black') +
  geom_col(aes(y = clearlowerbound, fill = 'Lower Clearance est.'), position = position_nudge(x = -0.16), width = .32, color = 'black') +
  coord_flip() + style1 +
  labs(y = 'Adherence and Clearance Rates', x = 'Treatment', title = 'Treatment Method vs. Adherence & Complete Clearance') +
  scale_y_continuous(labels = scales::percent) +
  scale_x_discrete(breaks = c("5-Fluorouracil (5%)", "Imiquimod (5%)", "Ingenol Mebutate (.015%)", "BF-200 10% ALA gel", "20% ALA solution"), labels = c("5-Fluorouracil (5%)", "Imiquimod (5%)", "Ingenol Mebutate (.015%)", "BF-200 10% ALA gel", "20% ALA solution")) + 
  scale_fill_manual('', breaks = c('Adherence', 'Upper Clearance est.', 'Lower Clearance est.'), values = c('darkorange2', 'dodgerblue4', 'dodgerblue'))

# Effective Cost vs. Treatment
ggplot(data_spread, aes(x = treatment)) +
  geom_col(aes(y = EC_upperbound, fill = 'Upper EC est.'), width = .7, color = 'black') +
  geom_col(aes(y = EC_lowerbound, fill = 'Lower EC est.'), width = .7, color = 'black') +
  style2 +
  scale_y_continuous(breaks = round(seq(0,4000,500)), labels = dollar) +
  scale_fill_manual('', breaks = c('Upper EC est.', 'Lower EC est.'), values = c('forestgreen', 'lawngreen')) +
  scale_x_discrete(breaks = c("5-Fluorouracil (5%)", "Imiquimod (5%)", "Ingenol Mebutate (.015%)", "BF-200 10% ALA gel", "20% ALA solution"), labels = c("5-Fluorouracil", "Imiquimod", "Ingenol Mebutate", "10% ALA", "20% ALA")) + 
  labs(y = 'Effective Cost', x = 'Treatment', title = 'Treatment Method vs. Effective Cost')
  
# image size: 1400 width, 575 height
  
