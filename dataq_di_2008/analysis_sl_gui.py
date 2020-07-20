#!/usr/bin/env python3
#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import epics
import epics.wx
from logging import debug,warn,info,error


import wx

__version__ = "0.0.0" #initial

class PanelTemplate(wx.Frame):

        title = "Dataq DI-2008 MATH"

        def __init__(self):
            wx.Frame.__init__(self, None, wx.ID_ANY, title=self.title, style=wx.DEFAULT_FRAME_STYLE)
            self.panel=wx.Panel(self, -1, size = (200,200))
            self.Bind(wx.EVT_CLOSE, self.OnQuit)

            self.initialize_GUI()
            self.SetBackgroundColour(wx.Colour(255,255,255))
            self.Centre()
            self.Show()

        def OnQuit(self,event):
            """
            orderly exit of Panel if close button is pressed
            """
            self.Destroy()
            del self

        def initialize_GUI(self):
            """
            """
            sizer = wx.GridBagSizer(hgap = 5, vgap = 5)
            self.label ={}
            self.field = {}
            self.sizer = {}
            main_sizer = wx.BoxSizer(wx.VERTICAL)
            topSizer = wx.BoxSizer(wx.VERTICAL)

            font = wx.Font(22, wx.ROMAN, wx.ITALIC, wx.NORMAL)
            for i in range(8):
                self.sizer[f'MATH{i}'] = wx.BoxSizer(wx.HORIZONTAL)
                self.label[f'MATH{i}'] = wx.StaticText(self.panel, label= f'MATH {i}:', style = wx.ALIGN_CENTER)
                self.field[f'MATH{i}'] = epics.wx.PVText(self.panel, pv=f'MacProBoxSL:MATH{i}',minor_alarm = wx.Colour(5, 6, 7),auto_units = True, size = (150,30));
                self.field[f'MATH{i}'].SetFont(font)
                self.label[f'MATH{i}'].SetFont(font)
                self.sizer[f'MATH{i}'].Add(self.label[f'MATH{i}'] , 0)
                self.sizer[f'MATH{i}'].Add(self.field[f'MATH{i}'] , 0)



            for i in range(8):
                main_sizer.Add(self.sizer[f'MATH{i}'],0)
                if (i==1) or (i==3) or (i==5) or (i==7):
                    main_sizer.Add(wx.StaticLine(self.panel), 30, wx.ALL|wx.EXPAND, 30)




            self.Center()
            self.Show()
            topSizer.Add(main_sizer,0)


            self.panel.SetSizer(topSizer)
            topSizer.Fit(self)
            self.Layout()
            self.panel.Layout()
            self.panel.Fit()
            self.Fit()

if __name__ == '__main__':
    from pdb import pm
    import logging
    from tempfile import gettempdir

    app = wx.App(redirect=False)
    panel = PanelTemplate()

    app.MainLoop()
