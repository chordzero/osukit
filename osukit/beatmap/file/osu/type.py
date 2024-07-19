from dataclasses import dataclass
from enum import Enum


class GameMode(Enum):
    OSU = 0
    TAIKO = 1
    CATCH = 2
    MANIA = 3

class OverlayPosition(Enum):
    NO_CHANGE = "NoChange"
    BELOW = "Below"
    ABOVE = "Above"

class EventType(Enum):
    BACKGROUNDS = 0
    VIDEOS = 1
    BREAKS = 2

class Effects(Enum):
    KIAI_ENABLED = 0
    SKIP_FIRST_BARLINE = 3

class HitSound(Enum):
    NORMAL = 0
    WHISTLE = 1
    FINISH = 2
    CLAP = 3

class SampleSet(Enum):
    NO_CUSTOM = 0
    NORMAL = 1
    SOFT = 2
    DRUM = 3

class HitObjectType:
    def __init__(self, i: int):
        self.bits = str(bin(i))[2:].zfill(8)

        self.circle     = self.bits[-1] == "1"
        self.slider     = self.bits[-2] == "1"
        self.new_combo  = self.bits[-3] == "1"
        self.spinner    = self.bits[-4] == "1"
        self.colour_hax = (self.bits[-5] == "1", self.bits[-6] == "1", self.bits[-7] == "1")
        self.hold       = self.bits[-8] == "1"

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.bits})"


@dataclass 
class HitSample:
    normalSet                : SampleSet = 0
    additionSet              : SampleSet = 0
    index                    : int = 0
    volume                   : int = 0
    filename                 : str = ""

@dataclass
class GeneralInfo:
    audioFilename            : str = None
    audioLeadIn              : int = 0
    previewTime              : int = -1
    countdown                : int = 1
    sampleSet                : str = "Normal"
    stackLeniency            : float = 0.7
    mode                     : GameMode = GameMode.OSU
    letterboxInBreaks        : bool = False
    useSkinSprites           : bool = False
    overlayPosition          : OverlayPosition = OverlayPosition.NO_CHANGE
    skinPreference           : str = None
    epilepsyWarning          : bool = False
    countdownOffset          : int = 0
    specialStyle             : bool = 0
    widescreenStoryboard     : bool = 0
    samplesMatchPlaybackRate : bool = 0
    
@dataclass
class EditorOption:
    bookmarks                : list[int] = None # Comma-separated list of integers
    distanceSpacing          : float = None
    beatDivisor              : int = None
    gridSize                 : int = None
    timelineZoom             : float = None

@dataclass
class Metadata:
    title                    : str = None
    titleUnicode             : str = None
    artist                   : str = None
    artistUnicode            : str = None
    creator                  : str = None
    version                  : str = None
    source                   : str = None
    tags                     : list[str] = None # Space-separated list of strings
    beatmapID                : int = None
    beatmapSetID             : int = None

@dataclass
class Difficulty:
    hpDrainRate              : float = None # 0.0 ~ 10.0
    circleSize               : float = None # 0.0 ~ 10.0
    overallDifficulty        : float = None # 0.0 ~ 10.0
    approachRate             : float = None # 0.0 ~ 10.0
    sliderMultiplier         : float = None
    sliderTickRate           : float = None

@dataclass
class Event:
    eventType                : EventType = None
    startTime                : int = None
    # eventParams              : dict[str, any] = None # Comma-separated list

    # def __getattr__(self, name):
    #     return getattr(self.eventParams, name)

@dataclass
class BackgroundEvent(Event):
    eventType                = EventType.BACKGROUNDS
    startTime                = 0
    fileName                 : str = None
    xOffset                  : int = 0
    yOffset                  : int = 0

@dataclass
class VideoEvent(Event):
    eventType                = EventType.VIDEOS
    startTime                : int = None
    fileName                 : str = None
    xOffset                  : int = 0
    yOffset                  : int = 0

@dataclass
class BreakEvent(Event):
    eventType                = EventType.BREAKS
    startTime                : int = None
    endTime                  : int = None    

@dataclass        
class TimingPoint:
    time                     : int = None
    beatLength               : int = None
    meter                    : int = None
    sampleSet                : SampleSet = None
    sampleIndex              : int = None
    volume                   : int = None
    uninherited              : bool = None
    effect                   : Effects = None

@dataclass
class Colours:
    sliderTrackOverride      : tuple[int, int, int] = None # rgb
    sliderBorder             : tuple[int, int, int] = None # rgb
    combos                   : dict[str, tuple[int, ...]] = None

@dataclass
class HitObject:
    # x,y,time,type,hitSound,objectParams,hitSample
    x                        : int = None
    y                        : int = None
    time                     : int = None
    type                     : HitObjectType = None
    hitSound                 : HitSound = None
    # objectParams             : list[any] = None # Comma-separated list
    hitSample                : HitSample = None

@dataclass
class HitCircle(HitObject):
    # x,y,time,type,hitSound,hitSample
    x                        : int = None
    y                        : int = None
    time                     : int = None
    type                     : HitObjectType = None
    hitSound                 : HitSound = None
    hitSample                : HitSample = None

@dataclass
class HitSlider(HitObject):
    class CurveType(Enum):
        BEZIER = "B"
        CATMULL = "C"
        LINEAR = "L"
        PERFECT = "P"


    # x,y,time,type,hitSound,curveType|curvePoints,slides,length,edgeSounds,edgeSets,hitSample
    x                        : int = None
    y                        : int = None
    time                     : int = None
    type                     : HitObjectType = None
    hitSound                 : HitSound = None
    curveType                : CurveType = None
    curvePoints              : list[tuple[int, int]] = None # Pipe(|)-separated list of strings
    slides                   : int = None
    length                   : int = None
    edgeSounds               : list[HitSound] = None # Pipe(|)-separated list of integers
    edgeSets                 : list[tuple[SampleSet, SampleSet]] = None # Pipe(|)-separated list of strings
    hitSample                : HitSample = None

@dataclass
class HitSpinner(HitObject):
    # x,y,time,type,hitSound,endTime,hitSample
    x                        : int = 256
    y                        : int = 192
    time                     : int = None
    type                     : HitObjectType = None
    hitSound                 : HitSound = None
    endTime                  : int = None
    hitSample                : HitSample = None
    
@dataclass
class HitHolds(HitObject):
    # x,y,time,type,hitSound,endTime:hitSample
    x                        : int = None # 0 <= floor(x * columnCount / 512) <= columnCount - 1
    y                        : int = 192
    time                     : int = None
    type                     : HitObjectType = None
    hitSound                 : HitSound = None
    endTime                  : int = None
    hitSample                : HitSample = None
