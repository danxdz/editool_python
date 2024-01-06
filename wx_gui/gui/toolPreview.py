import wx


tool_max_width = 520 # tool max width
tool_max_height = 220  # tool height
tool_box_margin = 10  # tool margin
text_spacer_w = 25 # space between text 
text_spacer_h = 10 # space between text 

def OnPaint(self, dc, tool):
        
        # Draw rectangles - tool sections
        def draw_rectangle(x, y, width, height):
                dc.DrawRectangle(int(x), int(y), int(width), int(height))

        brush = wx.Brush(wx.Brush(wx.Colour(240,240,240), wx.BRUSHSTYLE_SOLID))
        dc.SetBrush(brush)
        dc.SetPen(wx.Pen(wx.Colour((210,210,250)))) 

        dc.DrawRectangle(0, 0, tool_max_width+2*tool_box_margin, tool_max_height)
        dc.SetFont(self.font_name)

        dc.SetPen(wx.Pen('#0f0f0f'))
        dc.SetTextForeground(wx.Colour("black"))
        name_w, name_h = dc.GetTextExtent(str(tool.name))
        dc.DrawText(f"{tool.name} :: {self.toolData.tool_types_list[tool.toolType]}", int(tool_box_margin), 11)

         # Calculate scale factors
        w = 540
        axis_line = 150
        scale_width = w / tool.L3

        

        # Scale tool attributes
        scaled_values = {
            'D1': int(tool.D1 * scale_width)/2,
            'D2': int(tool.D2 * scale_width)/2 if tool.D2 else int(tool.D1 * scale_width)/2,
            'D3': int(tool.D3 * scale_width)/2,
            'L1': int(tool.L1 * scale_width),
            'L2': int(tool.L2 * scale_width) if tool.L2 else 0,
            'L3': int(tool.L3 * scale_width),
        }

        #for key, value in scaled_values.items():
        #    print(key, value)

        
        cut_len_border_color = wx.Colour("#6C3B12")
        cut_len_fill_color = wx.Colour("#C87A46")
        cut_len_border_pen = wx.Pen(cut_len_border_color, 1, wx.PENSTYLE_SOLID)
        cut_len_fill_brush = wx.Brush(cut_len_fill_color, wx.BRUSHSTYLE_SOLID)
        nocut_len_border_color = wx.Colour("dark gray")
        nocut_len_fill_color = wx.Colour("gray")
        nocut_len_border_pen = wx.Pen(nocut_len_border_color, 1, wx.PENSTYLE_SOLID)
        nocut_len_fill_brush = wx.Brush(nocut_len_fill_color, wx.BRUSHSTYLE_SOLID)


        # Draw rectangles

        dc.SetPen(nocut_len_border_pen)
        dc.SetBrush(nocut_len_fill_brush)
        # Need to center the tool neck, by find the dif between d1 and d2 and divide by 2
        dif = (scaled_values['D1'] - scaled_values['D2']) / 2
        draw_rectangle(scaled_values['L1']-1, axis_line + dif, scaled_values['L2']-scaled_values['L1']+1, -scaled_values['D2'])
        draw_rectangle(scaled_values['L2']-1, axis_line, scaled_values['L3']-scaled_values['L2']+1, -scaled_values['D3'])
        
        
        dc.SetPen(cut_len_border_pen)
        dc.SetBrush(cut_len_fill_brush)

        if tool.toolType == 0: 
            draw_rectangle(0, axis_line, scaled_values['L1']+1, -scaled_values['D1'])
        elif tool.toolType == 1:
            draw_rectangle(0, axis_line, scaled_values['L1']+1, -scaled_values['D1'])
            draw_rectangle(scaled_values['L1']-1, axis_line, scaled_values['L2']-scaled_values['L1']+1, -scaled_values['D2'])
        elif tool.toolType == 2:
            rad = int((scale_width*tool.cornerRadius))
            draw_rectangle(rad, axis_line, scaled_values['L1']-rad, -scaled_values['D1'])
            dc.DrawArc(rad, axis_line-rad,0, axis_line, rad, axis_line)
        elif tool.toolType == 3:
            draw_rectangle(0, axis_line, scaled_values['L1']+1, -scaled_values['D1'])
            draw_rectangle(scaled_values['L1']-1, axis_line, scaled_values['L2']-scaled_values['L1']+1, -scaled_values['D2'])

        # Draw axis line
        dc.SetPen(wx.Pen(wx.Colour("red"), 3, wx.DOT_DASH))
        dc.DrawLine(0, axis_line, 540, axis_line)

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

        # Draw tool parameters text        
        dc.SetFont(self.font_tool_params_12)
        dc.SetTextForeground(nocut_len_border_color)
        dc.DrawText('D1', m_l1-text_spacer_w, axis_line+text_spacer_h)
        dc.DrawText('L1', m_l1+text_spacer_w, axis_line+text_spacer_h)
        if tool.D2 and tool.D2 != 0:
            dc.DrawText('D2', m_l2-text_spacer_w, axis_line+text_spacer_h)
            dc.DrawText('L2', m_l2+text_spacer_w, axis_line+text_spacer_h)
        if tool.toolType == 2: 
            dc.DrawText('r', text_spacer_w, int(axis_line-(scaled_values['D1']*2)))
        dc.DrawText('D3', m_l3-text_spacer_w, axis_line+text_spacer_h)
        dc.DrawText('L3', m_l3+text_spacer_w, axis_line+text_spacer_h)

        dc.SetTextForeground(cut_len_border_color)
        dc.DrawText(str(tool.D1), m_l1-text_spacer_w-int(d1_w/4), axis_line+int(text_spacer_h*3))
        dc.DrawText(str(tool.L1), m_l1+text_spacer_w-int(l1_w/4), axis_line+int(text_spacer_h*3))
        if tool.D2 and tool.D2 != 0:
            dc.DrawText(str(tool.D2), m_l2-text_spacer_w-int(d2_w/4), axis_line+int(text_spacer_h*3))
            dc.DrawText(str(tool.L2), m_l2+text_spacer_w-int(l2_w/4), axis_line+int(text_spacer_h*3))
        if tool.toolType == 2:
            r_w, r_h = dc.GetTextExtent(str("r "))
            dc.DrawText(str(tool.cornerRadius), int(text_spacer_w+r_w+5), int(axis_line-(scaled_values['D1']*2)))

        dc.DrawText(str(tool.D3), m_l3-text_spacer_w-int(d1_w/4), axis_line+int(text_spacer_h*3))
        dc.DrawText(str(tool.L3), m_l3+text_spacer_w-int(l1_w/4), axis_line+int(text_spacer_h*3))
                    
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
        