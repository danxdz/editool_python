import wx
import math

tool_box_margin = 10  # tool margin
text_spacer_w = 30 # space between text 
text_spacer_h = 10 # space between text 

def OnPaint(self, dc, tool):
        #print("OnPaint", tool.name)    
        screen_width, screen_height = wx.GetDisplaySize()

        tool_max_width = int(screen_width/3)-20 # tool max width
        tool_max_height = int(screen_height/5)  # tool height

        # Draw rectangles - tool sections
        def draw_rectangle(x, y, width, height):
                dc.DrawRectangle(int(x), int(y), int(width), int(height))

        brush = wx.Brush(wx.Brush(wx.Colour(240,240,240), wx.BRUSHSTYLE_SOLID))
        dc.SetBrush(brush)
        dc.SetPen(wx.Pen(wx.Colour(200,200,200))) 

        dc.DrawRectangle(0, 0, tool_max_width-38, tool_max_height)
        dc.SetFont(self.font_name)

        dc.SetPen(wx.Pen('#0f0f0f'))
        dc.SetTextForeground(wx.Colour("black"))
        name_w, name_h = dc.GetTextExtent(str(tool.name))
        dc.DrawText(f"{tool.name} : {tool.z}z :: {self.toolData.tool_types_list[tool.toolType]}", int(tool_box_margin), 11)

         # Calculate scale factors
        axis_line = 160
        scale_width = (tool_max_width-40) / tool.L3


        # Scale tool attributes
        scaled_values = {
            'D1': int((tool.D1 * scale_width)/2),
            'D2': int((tool.D2 * scale_width)/2) if tool.D2 else int(((tool.D1-0.2) * scale_width)/2),
            'D3': int((tool.D3 * scale_width)/2),
            'L1': int(tool.L1 * scale_width),
            'L2': int(tool.L2 * scale_width) if tool.L2 else 0,
            'L3': int(tool.L3 * scale_width),
        }

        #print("scale_width", scale_width, scaled_values['L3'])

        rad = int(scaled_values['D1']) 
        corner_rad = int((scale_width*float(tool.cornerRadius)))


        #for key, value in scaled_values.items():
        #    print(key, value)

        
        cut_len_border_color = wx.Colour("#6C3B12")
        cut_len_fill_color = wx.Colour("#C87A46")
        cut_len_border_pen = wx.Pen(cut_len_border_color, 1, wx.PENSTYLE_SOLID)
        cut_len_fill_pen = wx.Pen(cut_len_fill_color, 1, wx.PENSTYLE_SOLID)
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

        if tool.D2 and tool.D2 != 0 and tool.L1 != tool.L2:
            # draw tool neck
            #draw_rectangle(scaled_values['L1']-1, axis_line, scaled_values['L2']-scaled_values['L1']+1, -scaled_values['D1']+int(0.2 * scale_width)/2)
            draw_rectangle(scaled_values['L1']-1, axis_line, scaled_values['L2']-scaled_values['L1']+1, -scaled_values['D2']+dif)

            # draw tool corps
            draw_rectangle(scaled_values['L2']-1, axis_line, scaled_values['L3']-scaled_values['L2']+1, -scaled_values['D3'])
        elif tool.L2 == 0:
            # draw tool corps    
            draw_rectangle(scaled_values['L1'], axis_line, scaled_values['L3']-scaled_values['L2']+1, -scaled_values['D3'])
        else:
            # draw tool neck
            draw_rectangle(scaled_values['L1']-1, axis_line, scaled_values['L2']-scaled_values['L1']+1, -scaled_values['D2']+dif)
            # draw tool corps
            draw_rectangle(scaled_values['L2']-1, axis_line, scaled_values['L3']-scaled_values['L2']+1, -scaled_values['D3'])
        
        
        dc.SetPen(cut_len_border_pen)
        dc.SetBrush(cut_len_fill_brush)
        # Draw tool sections
        # cut section
        if tool.toolType == 0: # endmill
            print('INFO : Drawing endmill')
            draw_rectangle(0, axis_line, scaled_values['L1']+1, -scaled_values['D1'])
            #print("scaled_values['L1']", scaled_values['L1'], "scaled_values['D1']", scaled_values['D1'])
        elif tool.toolType == 1: # radius
            print('INFO : Drawing radiusMill')
                
            dc.SetPen(cut_len_fill_pen)
            dc.SetBrush(cut_len_fill_brush)

            #calculate the center of the circle
            center_x = corner_rad
            #center = d1 - corner_rad
            center_y = int(- corner_rad + scaled_values['D1'])
            #calculate the start point of the circle
            p1_x = 0
            p1_y = int(-scaled_values['D1']+corner_rad)
            #calculate the end point of the circle
            p2_x = corner_rad
            p2_y = int(-scaled_values['D1'])



            dc.DrawArc(p2_x, axis_line + p2_y, p1_x, axis_line + p1_y, p2_x, axis_line + p1_y)
            #print("p1_x", p1_x, "p1_y", p1_y, "p2_x", p2_x, "p2_y", p2_y)
            draw_rectangle(p1_x, axis_line, scaled_values['L1']+1, p1_y)
            draw_rectangle(p2_x, axis_line, scaled_values['L1']-corner_rad+1, p2_y)
            print("p1_x", p1_x, "p1_y", p1_y, "p2_x", p2_x, "p2_y", p2_y)
            

        elif tool.toolType == 2: # ball
            print('INFO : Drawing ballMill')
            draw_rectangle(rad, axis_line, scaled_values['L1']-rad, -scaled_values['D1'])
            dc.DrawArc(rad, axis_line-rad,0, axis_line, rad, axis_line)
            #print("rad", rad, "scaled_values['L1']", scaled_values['L1'], "scaled_values['D1']", scaled_values['D1'])
            
            r_w, r_h = dc.GetTextExtent(str("r "))
            #dc.DrawText(str(tool.cornerRadius), int(text_spacer_w+r_w+5), int(axis_line-(scaled_values['D1']*2)))




        elif tool.toolType == 3 or tool.toolType == 7 : # chamfer
            print('INFO : Drawing chamferMill')

            #draw the chamfer line, that start at 0,0 and end at d1, and calc the angle
            len = int((scaled_values['D1']) / (math.tan(((float(tool.neckAngle)/2) * math.pi) / 180)))
            p1_x = 0
            p1_y = axis_line
            p2_x = len
            p2_y = axis_line - scaled_values['D1']
            p3_x = scaled_values['L1']
            p3_y = p2_y

            dc.DrawPolygon([(p1_x, p1_y), (p2_x, p2_y), (p3_x, p3_y), (p3_x, p1_y)])  
            print("p1_x", p1_x, "p1_y", p1_y, "p2_x", p2_x, "p2_y", p2_y, "p3_x", p3_x, "p3_y", p3_y)

        elif tool.toolType == 4: # tslot
            print('INFO : Drawing tslotMill')
            draw_rectangle(0, axis_line, scaled_values['L1']+1, -scaled_values['D1'])
            draw_rectangle(scaled_values['L1']-1, axis_line, scaled_values['L2']-scaled_values['L1']+1, -scaled_values['D2'])


        elif tool.toolType == 8: # threadMill
            print('INFO : Drawing threadMill')
            draw_rectangle(0, axis_line, scaled_values['L1']+1, -scaled_values['D1'])
            

        #find the middle of the tool l3, so we can draw the text in the middle of tool corps
        m_l1 = int((scaled_values['L1'])/2)
        m_l2 = int((scaled_values['L2'] - (scaled_values['L2']/2))+scaled_values['L1'])
        m_l3 = int((scaled_values['L3'] - scaled_values['L2'])/2)+scaled_values['L2']

        #get tool parameters text size
        d1_w, d1_h = dc.GetTextExtent(f"D1: {tool.D1}")
        d2_w, d2_h = dc.GetTextExtent(f"D2: {tool.D2}")
        d3_w, d3_h = dc.GetTextExtent(str(tool.D3))

        x_dl1 = m_l1-(int(d1_w/2))
        x_dl2 = m_l2-(int((d2_w/2)))
        x_dl3 = m_l3-(int(d3_w/2))

        #print("d1_w", d1_w, "d1_h", d1_h, "d2_w", d2_w, "d2_h", d2_h, "d3_w", d3_w, "d3_h", d3_h)         

        # Draw tool parameters labels        
        dc.SetFont(self.font_tool_params_12)
        dc.SetTextForeground(nocut_len_border_color)
        dc.DrawText('D1:', x_dl1, axis_line - int(scaled_values['D1'] + d1_h + text_spacer_h))
        dc.DrawText('L1:', x_dl1, axis_line + int(scaled_values['D1']/2))
        if scaled_values['D2'] > 0 and scaled_values['L2'] > scaled_values['L1']:
            dc.DrawText('D2:', x_dl2, axis_line - int(scaled_values['D2'] + d2_h + text_spacer_h))
            dc.DrawText('L2:', x_dl2, axis_line + int(scaled_values['D2']/2))
        #if tool.toolType == 2: 
            #dc.DrawText('r', text_spacer_w, int(axis_line-(scaled_values['D1']*2)))
        dc.DrawText('D3:', x_dl3, axis_line - int(scaled_values['D3'] + d3_h + text_spacer_h))
        dc.DrawText('L3:', x_dl3, axis_line + int(scaled_values['D3']/2))
        
        # Draw tool parameters values
        dc.SetTextForeground(cut_len_border_color)
        dc.DrawText(str(tool.D1), int(x_dl1+text_spacer_w), axis_line - int(scaled_values['D1'] + d1_h + text_spacer_h))
        dc.DrawText(str(tool.L1), int(x_dl1+text_spacer_w), axis_line + int(scaled_values['D1']/2))
        
        #if tool.D2 and tool.D2 != 0 and tool.L1 != tool.L2 or tool.L2 > tool.L1:
        if scaled_values['D2'] > 0 and scaled_values['L2'] > scaled_values['L1']:
            dc.DrawText(str(tool.D2), int(x_dl2+text_spacer_w), axis_line - int(scaled_values['D2'] + d2_h + text_spacer_h))
            dc.DrawText(str(tool.L2), int(x_dl2+text_spacer_w), axis_line + int(scaled_values['D2']/2))


        dc.DrawText(str(tool.D3), int(m_l3-(d3_w/2)+text_spacer_w), axis_line - int(scaled_values['D3'] + d3_h + text_spacer_h))
        dc.DrawText(str(tool.L3), int(m_l3-(d3_w/2)+text_spacer_w), axis_line + int(scaled_values['D3']/2))

        
        # Draw axis line
        dc.SetPen(wx.Pen(wx.Colour("red"), 3, wx.DOT_DASH))
        dc.DrawLine(0, axis_line, tool_max_width, axis_line)
                    
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
        