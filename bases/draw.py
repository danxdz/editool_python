import wxgl

app = wxgl.App()
app.cylinder((0,0,0), 1, 2)
app.title('快速体验:$x^2+y^2=1$')
app.show()