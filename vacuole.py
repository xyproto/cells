#!/usr/bin/env python
#-*-coding:utf8-*-

import sys
import time
import math
import pygame
from pygame.locals import *

try:
    import psyco
    psyco.full()
except ImportError:
    pass

class Cells:

    def __init__(self, surface, left, top, width, height, fg, bg, numcells_h=20, numcells_v=20, borderwidth=5):
        self.surface = surface
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.fg = fg
        self.bg = bg
        self.borderwidth = borderwidth
        # number of cells horizontally
        self.numcells_h = numcells_h
        # number of cells vertically
        self.numcells_v = numcells_v
        # width of cells
        self.cwidth = math.floor(float(self.width) / float(self.numcells_h))
        # height of cells
        self.cheight = math.floor(float(self.height) / float(self.numcells_v))
        # width of the cellmap
        self.width = self.cwidth * self.numcells_h
        # height of the cellmap
        self.height = self.cheight * self.numcells_v
        # center the cellmap horizontally
        self.left = left + (width - self.width) / 2
        # center the cellmap vertically
        self.top = top + (height - self.height) / 2
        # draw the background
        self.surface.fill(fg, (self.left - self.borderwidth, self.top - self.borderwidth, self.width + self.borderwidth * 2, self.height + self.borderwidth * 2))
        self.surface.fill(bg, (self.left, self.top, self.width, self.height))
        # the cells
        self.cells = {}
        # the drawing rect
        self.rect = (self.left, self.top, self.width, self.height)
        # read cellpatterns from file
        self.cellpatterns = {}
        self.cellpatternindex = None
        self.readcells("cells.txt")
        # the line we're at for doing cellular automa (vertical)
        self.cline = 0
        # use the active pattern
        self.putpattern()
        # font
        try:
            self.font = pygame.font.Font("vacuole.ttf", 24)
        except IOError:
            self.font = pygame.font.SysFont("Sans", 24)
        self.textfg = (255, 255, 255)
        self.textbg = (125, 193, 239)
        self.text = self.font.render(self.cellpatternindex, True, self.textfg, self.textbg)

    def readcells(self, filename):
        self.cellpatterns = {}
        lines = [line for line in open(filename).readlines() if line.strip() != '']
        linenr = 0
        cellname = lines[linenr].strip()
        while cellname:
            linenr += 1
            cellquestions = [question for question in lines[linenr].strip().split(' ') if question != '']
            linenr += 1
            cellanswers =  [answer for answer in lines[linenr].strip().split(' ') if answer != '']
            linenr += 1
            self.cellpatterns[cellname] = (cellquestions, cellanswers)
            try:
                cellname = lines[linenr].strip()
            except IndexError:
                break
        try:
            self.cellpatternindex = self.cellpatterns.keys()[0]
        except IndexError:
            print "Need at least one cellpattern in cells.txt"
            sys.exit(1)

    def next_cellpattern(self):
        keys = self.cellpatterns.keys()
        keys.sort()
        if self.cellpatternindex in keys:
            index = keys.index(self.cellpatternindex)
            if len(keys) == index + 1:
                index = 0
            else:
                index += 1
            self.cellpatternindex = keys[index]
        else:
            self.cellpatternindex = patterns[0]
        self.cellpatterntext()

    def cellpatterntext(self):
        self.text = self.font.render(self.cellpatternindex, True, self.textfg, self.textbg)

    def prev_cellpattern(self):
        keys = self.cellpatterns.keys()
        keys.sort()
        if self.cellpatternindex in keys:
            index = keys.index(self.cellpatternindex)
            if index == 0:
                index = len(keys) - 1
            else:
                index -= 1
            self.cellpatternindex = keys[index]
        else:
            self.cellpatternindex = patterns[0]
        self.cellpatterntext()

    def step(self):
        """run a cellpattern on the cells once"""
        questions, answers = self.cellpatterns[self.cellpatternindex]

        # find a question
        cell_line = "".join([str(int(self.bget(x, self.cline))) for x in xrange(self.numcells_h)])
        cell_line_length = len(cell_line)
        # for each column in the next line
        for nextcol in xrange(cell_line_length):
            # we wish to eximine the three cells that centers around this cells column
            if nextcol == 0:
                cells = "0" + cell_line[:2]
            elif nextcol == 1:
                cells = cell_line[:3]
            elif nextcol == cell_line_length - 2:
                # we are at the next-to-last cell of the row
                # we want the cells above to the left, above and above to the right
                cells = cell_line[cell_line_length-3:]
            elif nextcol == cell_line_length - 1:
                # we are at the last cell of the row
                # we want the two last cells of the row and "0"
                cells = cell_line[cell_line_length-2:] + "0"
            else:
                cells = cell_line[nextcol-1:nextcol+2]
            if len(cells) != 3:
                print "Wrong cell-length!", cells, nextcol
                sys.exit(3)
            if cells in questions:
                nextline = self.cline + 1
                if nextline == self.numcells_v:
                    nextline = 0
                nextlinevalue = bool(int(answers[questions.index(cells)]))
                #print cells, (nextcol, nextline), "=", nextlinevalue
                self.put(nextcol, nextline, nextlinevalue)
            else:
                print "No matching pattern for %s! Check your cell-file for cellpattern %s!"%(cells, self.cellpatternindex)
                sys.exit(2)

        # Wrap around when we've reached the last cell-line
        self.cline += 1
        if self.cline == self.numcells_v:
            self.cline = 0

    def clear(self):
        self.cells = {}
        self.cline = 0

    def put(self, x, y, color=True):
        if color == True:
            self.cells[(x, y)] = self.fg
        elif color == False:
            self.cells[(x, y)] = self.bg
        else:
            self.cells[(x, y)] = color

    def get(self, x, y):
        if (x, y) in self.cells:
            return self.cells[(x, y)]
        else:
            return self.bg

    def bget(self, x, y):
        return self.fg == self.get(x, y)

    def seed(self):
        self.put(math.floor(self.numcells_h / 2.0), 0, True)

    def putpattern(self):
        self.clear()
        self.seed()
        for i in range(self.numcells_v - 1):
            self.step()

    def draw(self):
        self.surface.fill(self.textbg)
        for y in xrange(self.numcells_v):
            for x in xrange(self.numcells_h):
                cell_left = self.left + int(x * self.cwidth)
                cell_top = self.top + int(y * self.cheight)
                cell_rect = (cell_left, cell_top, self.cwidth, self.cheight)
                pygame.draw.rect(self.surface, self.get(x, y), cell_rect, 0)
        self.surface.blit(self.text, (20, 2))

class Program:

    def __init__(self, width, height, bg, fg, splashtime=0.9, fullscreen=False, cells=20):
        self.numcells = cells
        self.width = width
        self.height = height
        self.bg = bg
        self.fg = fg

        pygame.display.init()
        pygame.font.init()

        if fullscreen:
            self.screen = pygame.display.set_mode((self.width, self.height), FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.width, self.height))

        pygame.display.set_caption("Vacuole")
        pygame.mouse.set_visible(1)

        self.clock = pygame.time.Clock()

        # --- Splash screen ---
        self.splashimage = None
        self.splash()
        pygame.display.flip()
        time.sleep(splashtime)

        # --- Contents ---

        self.borderwidth = 6
        self.margin = 20
        self.cells = Cells(self.screen, self.margin, self.margin, self.width - self.margin * 2, self.height - self.margin * 2, self.fg, self.bg, self.numcells, self.numcells, self.borderwidth)
        self.cells.draw()

        pygame.display.flip()

        # --- Mainloop ---
        self.wait_answer()

    def splash(self):
        if self.splashimage:
            scaled_image = self.splashimage
        else:
            image = pygame.image.load("vacuole.png")
            scaled_image = pygame.transform.scale(image, (self.width, self.height))
        return self.screen.blit(scaled_image, (0, 0))

    def wait_answer(self):
        keep_running = True

        # --- Mainloop ---
        while keep_running:

            for event in pygame.event.get():
                if event.type == QUIT:
                    keep_running = False
                elif event.type == KEYDOWN:
                    if event.key in [K_ESCAPE, K_q]:
                        keep_running = False
                    elif event.key == K_SPACE:
                        self.cells.step()
                        self.cells.draw()
                    elif event.key == K_RETURN:
                        self.cells.clear()
                        self.cells.seed()
                        self.cells.draw()
                    elif event.key == K_UP:
                        self.numcells += 1
                        cpi = self.cells.cellpatternindex
                        self.cells = Cells(self.screen, self.margin, self.margin, self.width - self.margin * 2, self.height - self.margin * 2, self.fg, self.bg, self.numcells, self.numcells, self.borderwidth)
                        self.cells.cellpatternindex = cpi
                        self.cells.putpattern()
                        self.cells.cellpatterntext()
                        self.cells.draw()
                    elif event.key == K_DOWN:
                        self.numcells -= 1
                        cpi = self.cells.cellpatternindex
                        self.cells = Cells(self.screen, self.margin, self.margin, self.width - self.margin * 2, self.height - self.margin * 2, self.fg, self.bg, self.numcells, self.numcells, self.borderwidth)
                        self.cells.cellpatternindex = cpi
                        self.cells.putpattern()
                        self.cells.cellpatterntext()
                        self.cells.draw()
                    elif event.key == K_LEFT:
                        self.cells.prev_cellpattern()
                        self.cells.putpattern()
                        self.cells.draw()
                    elif event.key == K_RIGHT:
                        self.cells.next_cellpattern()
                        self.cells.putpattern()
                        self.cells.draw()
                    #else:
                    #    print "bah", event.jey
                    else:
                        pass

            pygame.display.flip()

            #self.clock.tick(60)

def main():
    W = 1024
    H = 768
    FULL = False

    CELLS = 100

    BG = (255, 255, 220)
    FG = (5, 5, 10)

    SPLASH = 0.7

    p = Program(W, H, BG, FG, SPLASH, FULL, CELLS)

    pygame.display.quit()
    pygame.font.quit()
    print "All is well."
    sys.exit(0)

if __name__ == "__main__":
    main()
