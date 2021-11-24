## Restoration Patch Statistics Figure Maker
## By Professer H. Buckley and Ellis Nimick

# Outputs a single image containing 6 graphs, each displaying a spatial facet of gully-derived restoration patch habitats. 
# The percentage of selected gullies (for restoration) is plotted against patch area (ha), permiter:area, number of core areas, median core area per patch (ha), core:total patch area and nearest distance (m).
# This is iterated for gullies selected from a stream order of 2, 3 and 4.

library(tidyverse)
library(ggplot2)

dat.raw <- read.csv("TauArea_All_Collated.csv", header = T)
head(dat.raw)

sdat <- dat.raw %>%
  group_by(sub.no, stream.order, sub.pcnt) %>%
  mutate(core = ifelse(PatchLabel == "Core", 1, 0)) %>% 
  mutate(CoreArea = ifelse(CoreArea == 0, NA, CoreArea), CoreFullRatio = ifelse(CoreFullRatio == 0, NA, CoreFullRatio)) %>% 
  dplyr::select(sub.no, stream.order, sub.pcnt, core, NEAR_DIST, CoreArea, PerimAreaRatio, CoreFullRatio, Shape_Area) %>% 
  mutate(CoreArea = CoreArea/10000, Shape_Area = Shape_Area/10000) %>% 
  summarise(core = sum(core), NEAR_DIST = median(NEAR_DIST), CoreArea = median(CoreArea, na.rm = T), PerimAreaRatio = median(PerimAreaRatio), CoreFullRatio = median(CoreFullRatio, na.rm = T), Shape_Area = median(Shape_Area)) %>%
  group_by(stream.order, sub.pcnt) %>%
  dplyr::select(-sub.no) %>%
  summarise_all(list(Mean = mean)) %>%
  gather("metric", "value", -stream.order, -sub.pcnt)
  

sddat <- dat.raw %>%
  group_by(sub.no, stream.order, sub.pcnt) %>%
  mutate(core = ifelse(PatchLabel == "Core", 1, 0)) %>% 
  mutate(CoreArea = ifelse(CoreArea == 0, NA, CoreArea), CoreFullRatio = ifelse(CoreFullRatio == 0, NA, CoreFullRatio)) %>% 
  dplyr::select(sub.no, stream.order, sub.pcnt, core, NEAR_DIST, CoreArea, PerimAreaRatio, CoreFullRatio, Shape_Area) %>% 
  mutate(CoreArea = CoreArea/10000, Shape_Area = Shape_Area/10000) %>% 
  summarise(core = sum(core), NEAR_DIST = median(NEAR_DIST), CoreArea = median(CoreArea, na.rm = T), PerimAreaRatio = median(PerimAreaRatio), CoreFullRatio = median(CoreFullRatio, na.rm = T), Shape_Area = median(Shape_Area)) %>%
  group_by(stream.order, sub.pcnt) %>%
  dplyr::select(-sub.no) %>%
  summarise_all(list(SD = sd)) %>%
  gather("sd.metric", "sd.value", -stream.order, -sub.pcnt) %>%
  ungroup(.) %>%
  dplyr::select(-stream.order, -sub.pcnt)

gdat <- data.frame(sdat, sddat)

str(gdat)
head(gdat)
names(gdat)
levels(as.factor(gdat$metric))

my.cols <- c("#009E73", "#0072B2", "#D55E00")

gdat %>% 
  filter(metric != "Percent_core_Median_Mean") %>%
  mutate(metric = as.factor(metric)) %>%
  mutate(metric = fct_recode(metric, "Number of core areas" = "core_Mean", "Nearest distance (m)" = "NEAR_DIST_Mean", "Median core area per patch (ha)" = "CoreArea_Mean", "Perimeter:Area" = "PerimAreaRatio_Mean", "Core:Total patch area" = "CoreFullRatio_Mean", "Patch area (ha)" = "Shape_Area_Mean")) %>%
  mutate(metric = fct_relevel(metric, "Patch area (ha)", "Perimeter:Area", "Number of core areas", "Median core area per patch (ha)", "Core:Total patch area", "Nearest distance (m)")) %>%
  mutate(SE = 2 * sd.value/sqrt(100)) %>%
  ggplot(aes(x = as.factor(sub.pcnt), y = value, fill = stream.order, col = stream.order)) +
    geom_point(size = 3, shape = 21, alpha = 0.6) +
    geom_errorbar(aes(ymin = value - SE, ymax = value + SE), width = 0.1) +
    facet_wrap(metric ~ ., scales = "free", ncol = 2) +
    scale_fill_manual(values = my.cols, name = "Stream orders\nincluded in\ngully model") +
    scale_colour_manual(values = my.cols, name = "Stream orders\nincluded in\ngully model") +
    ylab("") +
    xlab("Percent of gullies selected") +
    theme_bw(base_size = 14) 
ggsave("Gully_facet_graph.png", height = 7, width = 9, dpi = 600)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
  
