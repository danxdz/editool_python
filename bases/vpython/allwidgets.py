import wx
from wxpyGL import wxglstream as gls
from wxpyGL import globject as glo

def main(parent):
    view = gls.basic_stream(parent, name='teapot')
    view.open()
    view.objects += [
        glo.Teapot(shade=glo.silver),
        glo.Sphere(shade=glo.water, pos=(0,1,0), size=0.5),
    ]
    view.handler.debug = 4
    return view

if __name__ == "__main__":
    app = wx.App()
    frm = wx.Frame(None)
    view = main(frm)
    frm.Show()
    app.MainLoop()