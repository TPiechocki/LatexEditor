#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author           : Tomasz Piechocki ( t.piechocki@yahoo.com )
# Created On       : 15.04.2019
# Last Modified By : Tomasz Piechocki ( t.piechocki@yahoo.com )
# Last Modified On : 19.05.2019
# Version          : 1.0
#
# Description      :
# Prosty edytor tekstu umożliwiający kompilowanie plików Latex.
#
# Licensed under GPL (see /usr/share/common-licenses/GPL for more details
# or contact # the Free Software Foundation for a copy)

import ntpath
import sys
import subprocess
import os, glob
import re
import argparse

from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QLabel, QInputDialog

from pathlib import Path

class Main(QtWidgets.QMainWindow):
    args = ""

    def __init__(self, parent=None):
        """ name of actual file """
        self.actual_file = ""

        #QtWidgets.QApplication.setStyle("Fusion")

        """ initialise Qt window """
        QtWidgets.QMainWindow.__init__(self, parent)

        """ widgets initialisations """
        self.text = QtWidgets.QTextEdit(self)
        self.menubar = self.menuBar()
        self.toolbar = self.addToolBar("Options")

        """ add widgets to the window and set window properties """
        self.initUI()

        if args.path:
            path = Path(args.path)
            if path.is_file() and args.path.endswith(".tex"):
                self.actual_file = args.path
                with open(self.actual_file, "rt") as file:
                    self.text.setText(file.read())
            else:
                print("Error: Plik nie istnieje lub jest niewłaściwego formatu(dopuszczalne pliki .tex). "
                      "Zostanie otwarty pusty plik.", file=sys.stderr)

    def initToolbar(self):
        """new file"""
        self.newAction = QtWidgets.QAction(QIcon.fromTheme("document-new"), "Nowy plik", self)
        self.newAction.setShortcut("Ctrl+N")
        self.newAction.triggered.connect(self.new)
        """open file"""
        self.openAction = QtWidgets.QAction(QIcon.fromTheme("document-open"), "Otwórz plik", self)
        self.openAction.setShortcut("Ctrl+O")
        self.openAction.triggered.connect(self.open)
        """save file"""
        self.saveAction = QtWidgets.QAction(QIcon.fromTheme("document-save"), "Zapisz", self)
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAction.triggered.connect(self.save)

        """ text cut """
        self.cutAction = QtWidgets.QAction(QIcon.fromTheme("edit-cut"), "Wytnij", self)
        self.cutAction.setShortcut(QKeySequence.Cut)
        self.cutAction.triggered.connect(self.text.cut)
        """ text copy """
        self.copyAction = QtWidgets.QAction(QIcon.fromTheme("edit-copy"), "Kopiuj", self)
        self.copyAction.setShortcut(QKeySequence.Copy)
        self.copyAction.triggered.connect(self.text.copy)
        """ text paste"""
        self.pasteAction = QtWidgets.QAction(QIcon.fromTheme("edit-paste"), "Wklej", self)
        self.pasteAction.setShortcut(QKeySequence.Paste)
        self.pasteAction.triggered.connect(self.text.paste)
        """ text undo """
        self.undoAction = QtWidgets.QAction(QIcon.fromTheme("edit-undo"), "Cofnij", self)
        self.undoAction.setShortcut(QKeySequence.Undo)
        self.undoAction.triggered.connect(self.text.undo)
        """ text redo """
        self.redoAction = QtWidgets.QAction(QIcon.fromTheme("edit-redo"), "Przywróć", self)
        self.redoAction.setShortcut(QKeySequence.Redo)
        self.redoAction.triggered.connect(self.text.redo)

        """ Latex actions """
        """ build file """
        self.buildAction = QtWidgets.QAction("Zbuduj plik" ,self)
        self.buildAction.setShortcut("Ctrl+B")
        self.buildAction.triggered.connect(self.build)
        """ open PDF """
        self.PDFAction = QtWidgets.QAction(QIcon.fromTheme("document-print-preview"), "Otwórz PDF", self)
        self.PDFAction.triggered.connect(self.openPDF)
        """ compress PDF """
        self.compressAction = QtWidgets.QAction("Kompresuj PDF", self)
        self.compressAction.triggered.connect(self.compressPDF)


        """
        Put icons in Toolbar
        """
        self.toolbar.addAction(self.copyAction)
        self.toolbar.addAction(self.cutAction)
        self.toolbar.addAction(self.pasteAction)

        self.toolbar.addSeparator()

        self.toolbar.addAction(self.undoAction)
        self.toolbar.addAction(self.redoAction)

    def initMenuBar(self):
        """
        initialise menu on top bar
        """
        file = self.menubar.addMenu("Plik")
        edit = self.menubar.addMenu("Edytuj")
        build = self.menubar.addMenu("Buduj")

        """
        File submenu
        """
        file.addAction(self.newAction)
        file.addAction(self.openAction)
        file.addAction(self.saveAction)

        """
        Edit submenu
        """
        edit.addAction(self.cutAction)
        edit.addAction(self.copyAction)
        edit.addAction(self.pasteAction)

        edit.addSeparator()

        edit.addAction(self.undoAction)
        edit.addAction(self.redoAction)

        """
        Build submenu
        """
        build.addAction(self.buildAction)
        build.addAction(self.PDFAction)
        build.addAction(self.compressAction)

    def initUI(self):
        """
        set widgets in window and window's properties
        """

        """ central part of window is text edit """
        self.setCentralWidget(self.text)

        self.initToolbar()

        """ add menu on top bar"""
        self.initMenuBar()

        """ window's properties """
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowTitle("Latex text editor")

    def new(self):
        self.save()
        self.hide()
        packages = []
        cancelled = False

        form = QtWidgets.QDialog()
        form.status_cancel = False

        """ packages to append to the new Latex file """
        packages_list = QtWidgets.QListWidget()
        package = QtWidgets.QPushButton()
        package.setText("Dodaj pakiet")
        def addItem():
            packages.append(QInputDialog.getText(self, 'Dodaj pakiet', 'Nazwa pakietu:')[0])
            packages_list.clear()
            packages_list.addItems(packages)
            form.repaint()
        package.clicked.connect(addItem)

        """ document class of new Latex document """
        document_class = QtWidgets.QComboBox()
        document_class.addItem("article")
        document_class.addItem("report")
        document_class.addItem("book")

        """ author and title """
        author = QtWidgets.QLineEdit()
        title = QtWidgets.QLineEdit()
        title_page = QtWidgets.QCheckBox()


        """ get basic info for Latex file template manager """
        main_layout = QtWidgets.QFormLayout()
        main_layout.addRow(QLabel("Autor:"), author)
        main_layout.addRow(QLabel("Tytuł:"), title)
        main_layout.addRow(QLabel("Strona tytułowa:"), title_page)
        main_layout.addRow(QLabel("Rodzaj dokumentu: "), document_class)
        main_layout.addRow(QLabel("Pakiety Latex: "), packages_list)
        main_layout.addRow(package)

        buttonBox = QtWidgets.QDialogButtonBox()
        buttonBox.addButton("Stwórz", QtWidgets.QDialogButtonBox.AcceptRole)
        buttonBox.addButton("Anuluj", QtWidgets.QDialogButtonBox.RejectRole)

        main_layout.addRow(buttonBox)
        buttonBox.accepted.connect(form.close)

        def cancel():
            form.close()
            form.status_cancel = True

        buttonBox.rejected.connect(cancel)
        form.setLayout(main_layout)
        form.exec_()

        form.repaint()

        """ return to the previous window if action cancelled """
        if form.status_cancel:
            self.show()
            return

        """ create with basic template manager """
        self.actual_file = ""
        new_doc = Main(self)
        new_doc.show()

        new_doc.text.clear()

        new_doc.text.insertPlainText("\documentclass{" + document_class.currentText() + "}\n\n")
        for it in packages:
            new_doc.text.insertPlainText("\\usepackage{" + it + "}\n")
        new_doc.text.insertPlainText("\n\\title{" + title.text() + "}\n"
                                        "\\author{" + author.text() + "}\n")
        new_doc.text.insertPlainText("\n\\begin{document}\n\n")
        if title_page.isChecked():
            new_doc.text.insertPlainText("\\maketitle\n")
        new_doc.text.insertPlainText("\n\end{document}")

    def open(self):
        """ Open file """
        self.actual_file = QtWidgets.QFileDialog.getOpenFileName(self, "Otwórz plik", ".", "TeX(*.tex *.sty)")[0]
        if self.actual_file:
            with open(self.actual_file, "rt") as file:
                self.text.setText(file.read())

    def save(self):
        """ save a current file or choose new name for it"""
        if not self.actual_file:  # if file is not set currently give an option to save it
            self.actual_file = QtWidgets.QFileDialog.getSaveFileName(self, "Zapisz plik", ".", "TeX(*.tex *.sty)")[0]

        if self.actual_file:  # if program knows filename
            if not self.actual_file.endswith((".tex", ".sty")):
                self.actual_file += ".tex"      # append tex extension if it's not added by user

            with open(self.actual_file, "wt") as file:
                file.write(self.text.toPlainText())

    def build(self):
        """
        build a TeX file
        File can't be in program location!
        """
        self.save() # save before build

        if self.actual_file:
            # check if OS can use command pdflatex
            pdflatex = subprocess.Popen("command -v pdflatex", stdout=subprocess.PIPE, shell=True)
            pdflatex = pdflatex.communicate()[0]

            if pdflatex:        # if OS has pdflatex
                output = ""
                error = ""
                command = "pdflatex -synctex=1 -interaction=nonstopmode '" + self.actual_file + "'"
                process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

                try:
                    # confirmation of action and info about no responsivity during compiling(maybe to do later with thread)
                    action_info = QtWidgets.QMessageBox.question(self, 'Buduj', "Czy chcesz kontynuować "
                                                                    "? W trakcie wykonania okno nie będzie reagowało",
                                                                    QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes,
                                                                    QtWidgets.QMessageBox.Yes)

                    if action_info == QtWidgets.QMessageBox.Yes:
                        output, error = process.communicate(timeout=10)      # compiling time out after 10 seconds
                except:
                    error = QtWidgets.QErrorMessage()
                    error.showMessage("Przekroczony limit czasu")
                    error.exec_()
                    return

                """ If Latex error occured show proper info about them """
                if "! " in str(output) or "No pages" in str(output):
                    basename = os.path.basename(self.actual_file)
                    logname = "./" + os.path.splitext(basename)[0] + ".log"

                    errors = "Plik nie został stworzony! <br><br>"

                    """ list errors from log """
                    with open(logname, 'r', encoding='latin-1') as log:
                        for line in log:
                            if "! " in line:
                                errors += "-----------------------<br>"
                                errors += line + "<br>"
                            elif line.startswith("l."):
                                errors += line + "<br>"

                    errors = re.sub(r"! ", "", errors)
                    errors = re.sub(r"l\.", "Line: ", errors)

                    """ show errors """
                    error = QtWidgets.QErrorMessage()
                    error.setWindowTitle("Błąd Latex")
                    error.showMessage(errors)
                    error.exec_()

                else:   # if pdf file was created
                    """ second time command for proper table of contents etc. """
                    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
                    output, error = process.communicate(timeout=10)

                    basename = os.path.basename(self.actual_file)
                    pdfname = "./" + os.path.splitext(basename)[0] + ".pdf"
                    pdfdest = os.path.splitext(self.actual_file)[0] + ".pdf"
                    os.rename(pdfname, pdfdest)     # move pdf file to tex location
                    self.openPDF()

                """ check if tex file is in the program location """
                texfile = glob.glob("./" + os.path.splitext(basename)[0] + ".tex")
                if texfile:
                    return

                """ if program directory is clear of tex file, remove temporary files """
                for filename in glob.glob("./" + os.path.splitext(basename)[0] + "*"):
                    os.remove(filename)


            else:      # if OS has no pdflatex software
                error = QtWidgets.QErrorMessage()
                error.showMessage("System nie posiada programu pdflatex. Proszę go zainstalować i spróbować ponownie.")
                error.exec_()

    def openPDF(self):
        """ open built file (if exists) in default pdf viewer; it works only for OS with xdg-open command working"""
        if self.actual_file:
            basename = os.path.splitext(self.actual_file)[0]
            pdfpath = Path(basename + ".pdf")

            # check if OS can use command xdg-open
            xdg = subprocess.Popen("command -v xdg-open", stdout = subprocess.PIPE, shell=True)
            xdg = xdg.communicate()[0]

            if pdfpath.is_file() and xdg:       # check if file exists and command can be used
                pdfpath = "xdg-open '" +  basename + ".pdf'"
                FNULL = open(os.devnull, 'w')
                open_PDF = subprocess.Popen(pdfpath, stdout=FNULL, stderr=subprocess.STDOUT ,shell=True)
                open_PDF.communicate()
            else:
                error = QtWidgets.QErrorMessage()
                error.showMessage("System nie obsługuje xdg-open lub nie istnieje taki plik(najpierw go zbuduj).")
                error.exec_()


        else:
            error = QtWidgets.QErrorMessage()
            error.showMessage("Obecny plik nie jest zapisany. Najpierw zapisz i go zbuduj.")
            error.exec_()

    def compressPDF(self):
        """ compres PDF using gs"""

        if self.actual_file:
            basename = os.path.splitext(self.actual_file)[0]
            pdfpath = Path(basename + ".pdf")

            # check if OS can use command gs
            gs = subprocess.Popen("command -v gs", stdout = subprocess.PIPE, shell=True)
            gs = gs.communicate()[0]

            if pdfpath.is_file() and gs:       # check if file exists and command can be used
                pdfpath = "gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/printer -dNOPAUSE -dQUIET -dBATCH -sOutputFile='" + basename + "_out.pdf' '" + basename + ".pdf'"
                FNULL = open(os.devnull, 'w')
                compress = subprocess.Popen(pdfpath,stdout=FNULL, stderr=subprocess.STDOUT, shell=True)
                compress.communicate()

                os.rename(basename + "_out.pdf", basename + ".pdf")     # rename file to first name
            else:
                error = QtWidgets.QErrorMessage()
                error.showMessage("System nie obsługuje gs lub nie istnieje taki plik PDF(najpierw go zbuduj).")
                error.exec_()

        else:
            error = QtWidgets.QErrorMessage()
            error.showMessage("Obecny plik nie jest zapisany. Najpierw zapisz i go zbuduj.")
            error.exec_()


def main():
    parser = argparse.ArgumentParser(description='Edytor plików tekstowych Latex.')
    parser.add_argument('-v', '--version', action='store_const', const='version', help="numer wersji")
    parser.add_argument('-o', '--open', type=str, dest='path',
                        help='otwarcie podanego pliku')

    global args
    args = parser.parse_args()
    if args.version:
        print("Wersja 1.0 stworzona przez Tomasza Piechockiego w 2019 roku.")
        sys.exit()

    app = QtWidgets.QApplication(sys.argv)

    window = Main()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
