from typing import Literal

EyeState = Literal["normal", "irritated", "covered", "damaged", "closed", "wide_open", "crying"]
EyeShape = Literal["almond", "round", "large_round", "ellipse", "narrow", "droopy", "sharp", "upturned", "downturned"]
GazeDirection = Literal["center", "up", "down", "left", "right", "upper_left", "upper_right", "lower_left", "lower_right"]
PupilShape = Literal["ellipse", "circle", "diamond", "vertical", "horizontal"]
IrisShape = Literal["circle", "ellipse", "hexagon", "octagon"]
ContourStyle = Literal["solid", "dashed", "double", "tapered"]
LashStyle = Literal["natural", "anime", "spiky", "ornate"]
LashForm = Literal["line", "tapered", "clustered", "disheveled"]
LowerLashStyle = Literal["natural", "anime", "spiky"]
BrowStyle = Literal["arched", "high_arch", "low_arch", "angular", "straight", "ornate", "long", "short", "thick", "dense", "faded", "inward"]
