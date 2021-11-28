import enum

@enum.unique
class DECISION_TYPES(enum.Enum):
    cut = 0
    mute = 1
    scene = 2
    commercial = 3
