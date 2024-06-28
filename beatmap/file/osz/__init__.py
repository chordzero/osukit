from ..osu import *
import zipfile

class OszFile:
    def __init__(self):
        self.beatmaps : list[OsuFile] = []
        pass

    def read(self, osz_path: str):
        self.beatmaps = []

        zip = zipfile.ZipFile(osz_path)
        for file in zip.filelist:
            if file.filename.endswith(".osu"):
                content = str(zip.read(file), encoding="utf-8")
                osu = OsuFile()
                osu.parse_str(content)
                self.beatmaps.append(osu)
                

        print(self.beatmaps)