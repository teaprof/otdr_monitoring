#!/bin/python3
import os, re, shutil


iconnames = ["clock", "network-connect", "configure", "go-next", "go-next-skip", "document-save", "application-exit",
             "document-export", "document-save-as", "tab-close", "labplot-xy-curve", "settings", "media-playlist-repeat", "go-last", "labplot-xy-curve-points",
             "edit-clear-history", "dialog-[a-z]*", "stop", "media-playback-stop", "labplot-xy-curve-segments", "labplot-xy-equation-curve", "dialog-error"]

SPstyleIcons = {"messagebox-question-icon": "question", "help": "question"}

iconnames.extend(SPstyleIcons.values())
             
iconmasks = [str + "\\..*" for str in iconnames] #append ".*" for iconnames
iconmasks.append("index.theme")

SPstyleMasks = {}
for key, value in SPstyleIcons.items():
    value = re.compile(value + "\\..*")
    SPstyleMasks[key] = value

resourcesRoot = '../../../3rdparty/icons/' 
#themes = [entry.name for entry in os.scandir(resourcesRoot) if entry.is_dir()]
themes = ["win11-blue"]
resourcesDest = './icons'

patterns = [re.compile(mask) for mask in iconmasks]

def findAllFiles(path):
    print(f"Searching icons in path {str(path)}")
    for entry in os.scandir(path):
        if entry.is_dir():
            yield from findAllFiles(entry.path)
        elif entry.is_file():
            yield entry

def isUsed(filename):
    for p in patterns:
        if p.fullmatch(filename) is not None:
            return True
    return False

def copy(theme, fullpath):
    relpath = os.path.relpath(fullpath, resourcesSource)
    relsrcfolder, _ = os.path.split(relpath)
    commonpath = os.path.commonpath([fullpath, resourcesSource])
    if commonpath == resourcesSource: #todo: del
        destFilePath = os.path.join(resourcesDest, theme, relpath)
        destFolderPath = os.path.join(resourcesDest, theme, relsrcfolder)
        #create folder if neccessary
        os.makedirs(destFolderPath, exist_ok=True)
        #copy file
        shutil.copyfile(fullpath, destFilePath)
    else:#todo: del 
        print(f'Can''t copy {fullpath}') #todo: del

def isUsedAsSPIcon(filename):
    keys = []
    for key, value in SPstyleMasks.items():
        if value.fullmatch(filename) is not None:
            keys.append(key)
    return keys

def copyAsSP(theme, fullpath, key):
    relpath = os.path.relpath(fullpath, resourcesSource)
    relsrcfolder, _ = os.path.split(relpath)
    _, ext = os.path.splitext(fullpath)
    commonpath = os.path.commonpath([fullpath, resourcesSource])
    if commonpath == resourcesSource:
        destFilePath = os.path.join(resourcesDest, theme, relsrcfolder, key+ext)
        destFolderPath = os.path.join(resourcesDest, theme, relsrcfolder)
        #create folder if neccessary
        os.makedirs(destFolderPath, exist_ok=True)
        #copy file
        shutil.copyfile(fullpath, destFilePath)
    else:
        print(f'Can''t copy {fullpath}')

if __name__ == '__main__':
    for theme in themes:
        resourcesSource = os.path.join(resourcesRoot, theme)
        for entry in findAllFiles(resourcesSource):
            if isUsed(entry.name):
                print(theme, ":", os.path.relpath(entry.path, resourcesSource))
                copy(theme, entry.path)
            keys = isUsedAsSPIcon(entry.name)
            if len(keys) > 0:
                for key in keys:
                    print(theme, ":", os.path.relpath(entry.path, resourcesSource))
                    copyAsSP(theme, entry.path, key)
