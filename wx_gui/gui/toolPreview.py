import wx


tool_max_width = 520 # tool max width
tool_max_height = 220  # tool height
tool_box_margin = 10  # tool margin
text_spacer = 20 # space between text 

def OnPaint(self, dc, tool):
        

        brush = wx.Brush(wx.Brush(wx.Colour(240,240,240), wx.BRUSHSTYLE_SOLID))
        dc.SetBrush(brush)
        dc.SetPen(wx.Pen(wx.Colour((210,210,250)))) 

        dc.DrawRectangle(0, 0, tool_max_width+2*tool_box_margin, tool_max_height)
        dc.SetFont(self.font_name)

        dc.SetPen(wx.Pen('#0f0f0f'))
        dc.SetTextForeground(wx.Colour("black"))
        w, h = dc.GetTextExtent(str(tool.name))
        dc.DrawText(f"{tool.name} :: {self.toolData.tool_types_list[tool.toolType]}", int(tool_box_margin), 11)

        def draw_rectangle(x, y, width, height):
                dc.DrawRectangle(int(x), int(y), int(width), int(height))


         # Calculate scale factors
        w = 540
        start_y = 150
        scale_width = w / tool.L3

        # Scale tool attributes
        scaled_values = {
            'D1': int(tool.D1 * scale_width)/2,
            'D2': int(tool.D2 * scale_width)/2 if tool.D2 else 0,
            'D3': int(tool.D3 * scale_width)/2,
            'L1': int(tool.L1 * scale_width),
            'L2': int(tool.L2 * scale_width) if tool.L2 else 0,
            'L3': int(tool.L3 * scale_width),
        }

        #for key, value in scaled_values.items():
        #    print(key, value)

        # Draw rectangles

        dc.SetPen(wx.Pen(wx.Colour("drak gray")))
        dc.SetBrush(wx.Brush(wx.Colour("gray"), wx.BRUSHSTYLE_SOLID))
        # Need to center the tool neck, by find the dif between d1 and d2 and divide by 2
        dif = (scaled_values['D1'] - scaled_values['D2']) / 2
        draw_rectangle(scaled_values['L1']-1, start_y + dif, scaled_values['L2']-scaled_values['L1']+1, -scaled_values['D2'])
        draw_rectangle(scaled_values['L2']-1, start_y, scaled_values['L3']-scaled_values['L2']+1, -scaled_values['D3'])

        if tool.toolType == 0: 
            dc.SetPen(wx.Pen(wx.Colour("orange")))
            dc.SetBrush(wx.Brush(wx.Colour("yellow"), wx.BRUSHSTYLE_SOLID))
            draw_rectangle(0, start_y, scaled_values['L1']+1, -scaled_values['D1'])
        elif tool.toolType == 1:
            dc.SetPen(wx.Pen(wx.Colour("orange")))
            dc.SetBrush(wx.Brush(wx.Colour("yellow"), wx.BRUSHSTYLE_SOLID))
            draw_rectangle(0, start_y, scaled_values['L1']+1, -scaled_values['D1'])
            dc.SetPen(wx.Pen(wx.Colour("orange")))
            dc.SetBrush(wx.Brush(wx.Colour("yellow"), wx.BRUSHSTYLE_SOLID))
            draw_rectangle(scaled_values['L1']-1, start_y, scaled_values['L2']-scaled_values['L1']+1, -scaled_values['D2'])
        elif tool.toolType == 2:
            dc.SetPen(wx.Pen(wx.Colour("orange")))
            dc.SetBrush(wx.Brush(wx.Colour("yellow"), wx.BRUSHSTYLE_SOLID))
            rad = int((scale_width*tool.cornerRadius))
            draw_rectangle(rad, start_y, scaled_values['L1']-rad, -scaled_values['D1'])
            dc.DrawArc(rad, start_y-rad,0, start_y, rad, start_y)

        elif tool.toolType == 3:
            dc.SetPen(wx.Pen(wx.Colour(("orange"))))
            dc.SetBrush(wx.Brush(wx.Colour("yellow"), wx.BRUSHSTYLE_SOLID))
            draw_rectangle(0, start_y, scaled_values['L1']+1, -scaled_values['D1'])
            dc.SetPen(wx.Pen(wx.Colour("orange")))
            dc.SetBrush(wx.Brush(wx.Colour("yellow"), wx.BRUSHSTYLE_SOLID))
            draw_rectangle(scaled_values['L1']-1, start_y, scaled_values['L2']-scaled_values['L1']+1, -scaled_values['D2'])

        # Draw axis line
        dc.SetPen(wx.Pen(wx.Colour("red"), 3, wx.DOT_DASH))
        dc.DrawLine(0, start_y, 540, start_y)


        # Draw tool
        dc.SetPen(wx.Pen('#0f0f0f'))
        dc.SetFont(self.font)
        
        #find the middle of the tool l3, so we can draw the text in the middle of tool corps
        m_l1 = int((scaled_values['L1']-0)/2)+0
        m_l2 = int((scaled_values['L2']-scaled_values['L1'])/2)+scaled_values['L1']
        m_l3 = int((scaled_values['L3']-scaled_values['L2'])/2)+scaled_values['L2']

        #get tool parameters text size
        d1_w, d1_h = dc.GetTextExtent(str(tool.D1))
        l1_w, l1_h = dc.GetTextExtent(str(tool.L1))
        d2_w, d2_h = dc.GetTextExtent(str(tool.D2))
        l2_w, l2_h = dc.GetTextExtent(str(tool.L2))
        d3_w, d3_h = dc.GetTextExtent(str(tool.D3))
        l3_w, l3_h = dc.GetTextExtent(str(tool.L3))


        

        dc.SetTextForeground(wx.Colour("black"))
        dc.DrawText('D1', m_l1-text_spacer, start_y+5)
        dc.DrawText('L1', m_l1+text_spacer, start_y+5)
        if tool.D2:
            dc.DrawText('D2', m_l2-text_spacer, start_y+5)
            dc.DrawText('L2', m_l2+text_spacer, start_y+5)
        if tool.toolType == 2: 
            dc.DrawText('r', text_spacer, int(start_y-(scaled_values['D1']*2)))
        dc.DrawText('D3', m_l3-text_spacer, start_y+5)
        dc.DrawText('L3', m_l3+text_spacer, start_y+5)

        dc.SetTextForeground(wx.Colour("orange"))
        dc.DrawText(str(tool.D1), m_l1-text_spacer-int(d1_w/4), start_y+20)
        dc.DrawText(str(tool.L1), m_l1+text_spacer-int(l1_w/4), start_y+20)
        if tool.D2:
            dc.DrawText(str(tool.D2), m_l2-text_spacer-int(d2_w/4), start_y+20)
            dc.DrawText(str(tool.L2), m_l2+text_spacer-int(l2_w/4), start_y+20)
        if tool.toolType == 2:
            r_w, r_h = dc.GetTextExtent(str("r "))
            dc.DrawText(str(tool.cornerRadius), int(text_spacer+r_w+5), int(start_y-(scaled_values['D1']*2)))

        dc.DrawText(str(tool.D3), m_l3-text_spacer-int(d1_w/4), start_y+20)
        dc.DrawText(str(tool.L3), m_l3+text_spacer-int(l1_w/4), start_y+20)
                    
        '''# Draw tool lines
        dc.SetPen(wx.Pen('#0f0f0f'))
        dc.DrawLine(0, 0, 0, scaled_values['D1'])
        dc.DrawLine(0, scaled_values['D1'], scaled_values['L1'], scaled_values['D1'])
        dc.DrawLine(scaled_values['L1'], scaled_values['D1'], scaled_values['L1'], scaled_values['D2'])
        dc.DrawLine(scaled_values['L1'], scaled_values['D2'], scaled_values['L2'], scaled_values['D2'])
        dc.DrawLine(scaled_values['L2'], scaled_values['D2'], scaled_values['L2'], scaled_values['D3'])
        dc.DrawLine(scaled_values['L2'], scaled_values['D3'], scaled_values['L3'], scaled_values['D3'])
        dc.DrawLine(scaled_values['L3'], scaled_values['D3'], scaled_values['L3'], 0)
        dc.DrawLine(scaled_values['L3'], 0, 0, 0)'''
        