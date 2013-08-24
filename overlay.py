import wx 
import random
from PIL import Image
import numpy

import rec

LOW_RPM = 5
HIGH_RPM = 30

class FancyFrame(wx.Frame): 
    def __init__(self, width, height): 
        wx.Frame.__init__(self, None, style = wx.STAY_ON_TOP | wx.FRAME_NO_TASKBAR | wx.FRAME_SHAPED, size=(width, height)) 
        self.SetTransparent(0)
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyDown) 
        self.Bind(wx.EVT_SIZE, self.OnSize)
  
        # OnSize called to make sure the buffer is initialized.
        # This might result in OnSize getting called twice on some
        # platforms at initialization, but little harm done.
        self.OnSize(None)
        
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)
            
        self.measure = rec.Measure()
        self.measure.start()
        
        self.timer.Start(400)
        
        self.Show(True) 

    def StartDisturbing(self):
        self.timer.Start(400)
        
    def StopDisturbing(self):
        self.timer.Stop()
        
    def OnSize(self,event):
        # The Buffer init is done here, to make sure the buffer is always
        # the same size as the Window
        Size  = self.ClientSize

        # Make new offscreen bitmap: this bitmap will always have the
        # current drawing in it, so it can be used to save the image to
        # a file, or whatever.
        self._Buffer = wx.EmptyBitmap(*Size)
        self.UpdateDrawing()
        
    def UpdateDrawing(self):
        """
        This would get called if the drawing needed to change, for whatever reason.

        The idea here is that the drawing is based on some data generated
        elsewhere in the system. If that data changes, the drawing needs to
        be updated.

        This code re-draws the buffer, then calls Update, which forces a paint event.
        """
        dc = wx.MemoryDC()
        dc.SelectObject(self._Buffer)
        self.Draw(dc)
        del dc # need to get rid of the MemoryDC before Update() is called.
        self.Refresh()
        self.Update()
        
    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self, self._Buffer)
        
    def Draw(self, dc):
        w, h = self.GetSize()
        
        data = numpy.random.rand(w, h, 3) * 255
        img = Image.fromarray(data.astype('uint8')).convert('RGB')
        # for x in range(w):
            # for y in range(h):
                # intensity = random.randrange(0, 256)
                # img.putpixel((x, y), (intensity, intensity, intensity))
        bm = wx.BitmapFromBuffer(w, h, img.tostring())
        dc.DrawBitmap(bm, 0, 0)
                
    def OnKeyDown(self, event): 
        """quit if user press Esc""" 
        if event.GetKeyCode() == 27:
            self.Close(force=True) 
        else: 
            event.Skip() 
            
    def update(self, event):
        rpm = self.measure.get_rpm()
        print 'RPM =', rpm
        
        tranperancy = int(255 - 255.0 * (rpm - LOW_RPM) / (HIGH_RPM - LOW_RPM))
        if tranperancy < 0:
            tranperancy = 0
        if tranperancy > 255:
            tranperancy = 255
        self.SetTransparent(tranperancy)
        if tranperancy > 0:
            self.UpdateDrawing()

if __name__ == "__main__": 
    app = wx.App(False) 
    screenSize = wx.DisplaySize()
    f = FancyFrame(*screenSize) 
    app.MainLoop() 