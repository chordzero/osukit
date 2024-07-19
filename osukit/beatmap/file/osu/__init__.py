from .type import *

import dataclasses
import re


class OsuFile:
    def __init__(self):
        self.formatVersion  : str = None
        self.general        : GeneralInfo = GeneralInfo()
        self.editor         : EditorOption = EditorOption()
        self.metadata       : Metadata = Metadata()
        self.difficulty     : Difficulty = Difficulty()
        self.events         : list[Event] = []
        self.timingPoints   : list[TimingPoint] = []
        self.colours        : Colours = Colours()
        self.hitObjects     : list[HitObject] = []


    # 각 카테고리 내용물만 반환
    def _get_block_contents(self, raw_data: str, block_name: str) -> list[str]:
        for block in raw_data.strip().split("["):
            if block.startswith(block_name + "]"):
                return block.split("\n")[1:]
                

    def _parse_block(self, raw_data: str, block_name: str):
        block = self._get_block_contents(raw_data, block_name)
        fields = dataclasses.fields(getattr(self, block_name.lower()))

        for line in block:
            kv = [i.strip() for i in line.split(":")]
            if len(kv) < 2:
                continue

            if key := next(key for key in fields if key.name.lower() == kv[0].lower()):
                if issubclass(key.type, Enum):
                    kv[1] = type([i.value for i in key.type][0])(kv[1])

                setattr(getattr(self, block_name.lower()), key.name, key.type(kv[1]))
        


    def parse_str(self, raw_data: str):
        # osu file format version
        if regex := re.match(r"osu file format v(?P<version>.+)", raw_data, flags=re.M|re.S):
            self.formatVersion = regex.group("version")

        self._parse_block(raw_data, "General")
        self._parse_block(raw_data, "Editor")
        self._parse_block(raw_data, "Metadata")
        self._parse_block(raw_data, "Difficulty")

        # colours
        combos = {}
        for kv_str in self._get_block_contents(raw_data, "Colours"):
            kv = [i.strip() for i in kv_str.split(":")]
            if len(kv) < 2:
                continue

            if regex := re.match(r"Combo(?P<idx>\d+)", kv[0], flags=re.M|re.S):
                combos[regex.group("idx")] = (int(i) for i in kv[1].split(","))
            else:
                key = kv[0][0].lower() + kv[0][1:]
                setattr(self.colours, key, (int(i) for i in kv[1].split(",")))
        self.colours.combos = combos

        # events
        for data in self._get_block_contents(raw_data, "Events"):
            comma_frag = data.split(",")
            match comma_frag[0]:
                case EventType.BACKGROUNDS.value:
                    self.events.append(BackgroundEvent(
                        fileName=comma_frag[2],
                        xOffset=int(comma_frag[3]),
                        yOffset=int(comma_frag[4])
                    ))
                case EventType.VIDEOS.value:
                    self.events.append(VideoEvent(
                        startTime=int(comma_frag[1]),
                        fileName=comma_frag[2],
                        xOffset=int(comma_frag[3]),
                        yOffset=int(comma_frag[4])
                    ))
                case EventType.BREAKS.value:
                    self.events.append(BreakEvent(
                        startTime=int(comma_frag[1]),
                        endTime=int(comma_frag[2])
                    ))

        # timing point
        for data in self._get_block_contents(raw_data, "TimingPoints"):
            comma_frag = data.split(",")
            if len(comma_frag) != 8:
                continue

            self.timingPoints.append(TimingPoint(
                time=round(float(comma_frag[0])),
                beatLength=int(float(comma_frag[1])),
                meter=int(comma_frag[2]),
                sampleSet=SampleSet(int(comma_frag[3])),
                sampleIndex=int(comma_frag[4]),
                volume=int(comma_frag[5]),
                uninherited=bool(comma_frag[6]),
                effect=Effects(int(comma_frag[7]))
            ))

        # hit object
        list_strip = lambda s: s.strip()
        for hit in self._get_block_contents(raw_data, "HitObjects"):
            # HitCircle  6  : x,y,time,type,hitSound,hitSample
            # HitSlider  11 : x,y,time,type,hitSound,curveType|curvePoints,slides,length,edgeSounds,edgeSets,hitSample
            # HitSpinner 7  : x,y,time,type,hitSound,endTime,hitSample
            # HitHolds   6  : x,y,time,type,hitSound,endTime:hitSample
            comma_frag = hit.split(",")
            colon_frag = hit.split(":")
            lcomma = len(comma_frag)
            lcolon = len(colon_frag)

            # Slider
            if "|" in hit:
                s = comma_frag[5].split("|")
                self.hitObjects.append(HitSlider(
                    x=int(comma_frag[0]),
                    y=int(comma_frag[1]),
                    time=int(comma_frag[2]),
                    type=HitObjectType(int(comma_frag[3])),
                    hitSound=HitSound(int(comma_frag[4])),
                    curveType=HitSlider.CurveType(s[0]),
                    curvePoints=[tuple(i.split(":")) for i in s[1:]],
                    slides=int(comma_frag[6]),
                    length=int(comma_frag[7]),
                    edgeSounds=[HitSound(int(i)) for i in comma_frag[8].split("|")],
                    edgeSets=[(SampleSet(int(s)) for s in i.split(":")) for i in comma_frag[9].split("|")],
                    hitSample=HitSample(*map(list_strip, comma_frag[10].split(":")))
                ))
            # Circle
            elif lcomma == 6 and lcolon == 5:
                self.hitObjects.append(HitCircle(
                    x=int(comma_frag[0]),
                    y=int(comma_frag[1]),
                    time=int(comma_frag[2]),
                    type=HitObjectType(int(comma_frag[3])),
                    hitSound=HitSound(int(comma_frag[4])),
                    hitSample=HitSample(*map(list_strip, comma_frag[5].split(":")))
                ))
            # Spinner
            elif lcomma == 7 and lcolon == 5:
                self.hitObjects.append(HitSpinner(
                    x=int(comma_frag[0]),
                    y=int(comma_frag[1]),
                    time=int(comma_frag[2]),
                    type=HitObjectType(int(comma_frag[3])),
                    hitSound=HitSound(int(comma_frag[4])),
                    endTime=int(comma_frag[5]),
                    hitSample=HitSample(*map(list_strip, comma_frag[6].split(":")))
                ))
            # Hold
            elif lcomma == 6 and lcolon == 6:
                s = comma_frag[5].split(":")
                self.hitObjects.append(HitHolds(
                    x=int(comma_frag[0]),
                    y=int(comma_frag[1]),
                    time=int(comma_frag[2]),
                    type=HitObjectType(int(comma_frag[3])),
                    hitSound=HitSound(int(comma_frag[4])),
                    endTime=int(s[0]),
                    hitSample=HitSample(*map(list_strip, s[1:]))
                ))
