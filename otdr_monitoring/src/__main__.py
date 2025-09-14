from gui.mainwindow.mainwindow import MainWindow
from PySide6.QtWidgets import QApplication

from PySide6.QtGui import QIcon
from PySide6.QtCore import QResource

import os
os.environ["PATH"] += os.pathsep + "." #path to libusb-1.0.dll, in Linux does nothing

import cProfile, pstats, io
from pstats import SortKey


def main():
    app = QApplication()
    theme_search_paths = QIcon.themeSearchPaths()
    QIcon.setThemeSearchPaths([":/icons"]+theme_search_paths)
    ##app.setDesktopSettingsAware(False)
    QResource.registerResource("./gui/monitoringrc.rcc")
    QIcon.setThemeName("win11-blue")
    app.setStyle("win11-blue")
    
    mainWindow = MainWindow()
    app.exec()

def profile():
    pr = cProfile.Profile()
    pr.enable()
    main()
    pr.disable()
    #pr.print_stats(sort="calls")
    pr.dump_stats("dupFinder.prof")
    #gui.filetreebrowser.simpletreemodelexample.test()
    s = io.StringIO()
    sortby = SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream = s).strip_dirs().sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())
    os.system('snakeviz dupFinder.prof')

if __name__=="__main__":
    main()
    #profile()



