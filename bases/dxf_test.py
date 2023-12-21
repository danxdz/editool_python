import ezdxf

doc = ezdxf.readfile("C:/Users/daniel.mendesdeamori/Downloads/editool_python/bases/tst.dxf")

print  (doc)

msp = doc.modelspace()

print (msp)

for e in msp:
    print (e)

psp = doc.paperspace("Layout1")

for e in psp:
    print (e)
    print (e.get_app_data())

blk = doc.blocks.get("#25F")

print (blk)