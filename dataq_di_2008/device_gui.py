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

        title = "Dataq DI-2008"

        def __init__(self):
            wx.Frame.__init__(self, None, wx.ID_ANY, title=self.title, style=wx.DEFAULT_FRAME_STYLE)
            self.panel=wx.Panel(self, -1, size = (200,75))
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



            self.sizer[b'dio'] = wx.BoxSizer(wx.HORIZONTAL)
            self.label[b'dio'] = wx.StaticText(self.panel, label= 'DIO:', style = wx.ALIGN_CENTER)
            self.field[b'dio'] = epics.wx.PVText(self.panel, pv='MacProBox:DIO',minor_alarm = wx.Colour(5, 6, 7),auto_units = True, size = (100,20))
            self.sizer[b'dio'].Add(self.label[b'dio'] , 0)
            self.sizer[b'dio'].Add(self.field[b'dio'] , 0)

            for i in range(8):
                self.sizer[f'aio{i}'] = wx.BoxSizer(wx.HORIZONTAL)
                self.label[f'aio{i}'] = wx.StaticText(self.panel, label= f'AIO{i}:', style = wx.ALIGN_CENTER)
                self.field[f'aio{i}'] = epics.wx.PVText(self.panel, pv=f'MacProBox:CH{i}',minor_alarm = wx.Colour(5, 6, 7),auto_units = True, size = (100,20))
                self.sizer[f'aio{i}'].Add(self.label[f'aio{i}'] , 0)
                self.sizer[f'aio{i}'].Add(self.field[f'aio{i}'] , 0)



            for i in range(8):
                main_sizer.Add(self.sizer[f'aio{i}'],0)
                if (i==1) or (i==3) or (i==5) or (i ==7):
                    main_sizer.Add(wx.StaticLine(self.panel), 20, wx.ALL|wx.EXPAND, 20)
            main_sizer.Add(self.sizer[b'dio'],0)



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
