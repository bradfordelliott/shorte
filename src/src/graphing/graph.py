#!/usr/bin/python
import sys
import re
sys.path.append("../../libs")
sys.path.append("libs")
import cairo_access
from cairo_access import *
import math

class cairo_t():
    def __init__(self, width, height):
        self.image = cairo(5000, 5000)

    def draw_text(self, x, y, text, font_color="black", text_anchor="start", angle=0, font_size=10, text_orientation="horizontal"):
        font_color = self.translate_color(font_color)
    
        width = 0
    
        font_size += 3
    
        #$self->drawRect({"x" => $propsRef->{"x"},
        #                 "y" => $propsRef->{"y"},
        #                 "width" => $propsRef->{"width"},
        #                 "height" => $propsRef->{"height"},
        #                 "line-color" => "#000000",
        #                 "background-color" => "#FFFFFF"});
                         
        self.image.set_font_size(font_size)
        (text_width, text_height) = self.image.text_extents("%s" % text)
        self.image.save()
        
        if(text_orientation == "horizontal"):
            if(text_anchor == "start"):
                self.image.move_to(x, y + text_height)
            elif(text_anchor == "middle"):
                self.image.move_to(x + width/2 - (text_width/2), y + text_height)
            else:
                self.image.move_to(x + width - text_width, y + text_height)
        else:
            if(text_anchor == "middle"):
                self.image.move_to(x, y + text_height/2)
            else:
                self.image.move_to(x, y + text_height)
            self.image.rotate(-(3.14/2))
        
        self.image.set_source_rgb(font_color[0], font_color[1], font_color[2])
        
        self.image.show_text("%s" % text)
        self.image.stroke()
        self.image.restore()

    def draw_rect(self, x, y, width, height, text=None, background_color="white", line_color="black"):

        self.image.set_line_width(1);
        rounding=0
        text="test"

        background_color = self.translate_color(background_color)
        line_color = self.translate_color(line_color)
        font_color = line_color
        font_size = 10
        angle = 0
        text_orientation="horizontal"
        
        if(rounding):
            pass
            #my $radius = $propsRef->{"rounding"};
            #my $x0 = $propsRef->{"x"};
            #my $y0 = $propsRef->{"y"};
            #my $x1 = $x0 + $propsRef->{"width"};
            #my $y1 = $y0 + $propsRef->{"height"};
            #my $rect_width = $propsRef->{"width"};
            #my $rect_height = $propsRef->{"height"};
            #
            #if ($rect_width/2<$radius)
            #{
            #    if ($rect_height/2<$radius)
            #    {
            #        $im->move_to  ($x0, ($y0 + $y1)/2);
            #        $im->curve_to ($x0 ,$y0, $x0, $y0, ($x0 + $x1)/2, $y0);
            #        $im->curve_to ($x1, $y0, $x1, $y0, $x1, ($y0 + $y1)/2);
            #        $im->curve_to ($x1, $y1, $x1, $y1, ($x1 + $x0)/2, $y1);
            #        $im->curve_to ($x0, $y1, $x0, $y1, $x0, ($y0 + $y1)/2);
            #    }
            #    else
            #    {
            #        $im->move_to  ($x0, $y0 + $radius);
            #        $im->curve_to ($x0 ,$y0, $x0, $y0, ($x0 + $x1)/2, $y0);
            #        $im->curve_to ($x1, $y0, $x1, $y0, $x1, $y0 + $radius);
            #        $im->line_to ($x1 , $y1 - $radius);
            #        $im->curve_to ($x1, $y1, $x1, $y1, ($x1 + $x0)/2, $y1);
            #        $im->curve_to ($x0, $y1, $x0, $y1, $x0, $y1- $radius);
            #    }
            #}
            #else
            #{
            #    if ($rect_height/2<$radius)
            #    {
            #        $im->move_to  ($x0, ($y0 + $y1)/2);
            #        $im->curve_to ($x0 , $y0, $x0 , $y0, $x0 + $radius, $y0);
            #        $im->line_to ($x1 - $radius, $y0);
            #        $im->curve_to ($x1, $y0, $x1, $y0, $x1, ($y0 + $y1)/2);
            #        $im->curve_to ($x1, $y1, $x1, $y1, $x1 - $radius, $y1);
            #        $im->line_to ($x0 + $radius, $y1);
            #        $im->curve_to ($x0, $y1, $x0, $y1, $x0, ($y0 + $y1)/2);
            #    }
            #    else
            #    {
            #        $im->move_to  ($x0, $y0 + $radius);
            #        $im->curve_to ($x0 , $y0, $x0 , $y0, $x0 + $radius, $y0);
            #        $im->line_to ($x1 - $radius, $y0);
            #        $im->curve_to ($x1, $y0, $x1, $y0, $x1, $y0 + $radius);
            #        $im->line_to ($x1 , $y1 - $radius);
            #        $im->curve_to ($x1, $y1, $x1, $y1, $x1 - $radius, $y1);
            #        $im->line_to ($x0 + $radius, $y1);
            #        $im->curve_to ($x0, $y1, $x0, $y1, $x0, $y1- $radius);
            #    }
            #}
            #$im->close_path ();

            #$im->set_source_rgb ($propsRef->{"background-color"}->[0], $propsRef->{"background-color"}->[1], $propsRef->{"background-color"}->[2]);
            #$im->fill_preserve ();
            #$im->set_source_rgb ($propsRef->{"line-color"}->[0], $propsRef->{"line-color"}->[1], $propsRef->{"line-color"}->[2]);
            #$im->stroke ();
        else:
            self.image.set_source_rgb(background_color[0], background_color[1], background_color[2])
            self.image.rectangle(x,y,width,height)
            self.image.fill()
            
            self.image.set_source_rgb(line_color[0], line_color[1], line_color[2])
            self.image.rectangle(x,y,width,height)
            self.image.stroke()
        
        if(text != None):
           self.draw_text(
                   x = x + width/2,
                   y = y + height/3,
                   text = text,
                   font_color = font_color,
                   font_size = font_size,
                   angle = angle,
                   #width = width,
                   #height = height,
                   text_anchor = "middle",
                   text_orientation = text_orientation)
               

    def draw_ellipse(self, x, y, width, height,
                    line_pattern=1,
                    font_color="#00000",
                    font_size=10,
                    text=None,
                    line_color="#000000",
                    background_color="#ffffff"):
        im = self.image
        
        line_color = self.translate_color(line_color)
        background_color = self.translate_color(background_color)
        font_color = self.translate_color(font_color)
        
        im.set_line_width(0.6);
        
        im.save();
        im.translate(x + width / 2.,
                     y + height / 2.);
        im.scale(1. * (width / 2.), 1. * (height / 2.));
        im.arc(0., 0., 1., 0., 2 * 3.1457);
        
        im.set_source_rgb(background_color[0], background_color[1], background_color[2]);
        im.fill_preserve();
        im.restore();
        
        im.set_source_rgb(line_color[0], line_color[1], line_color[2]);
        im.stroke();
        
        if(text != None):
           self.draw_text(
               x = x,
               y = y + height/3,
               text = text,
               font_color = font_color,
               font_size = font_size,
               angle = angle,
               width = width,
               height = height,
               text_anchor = "middle",
               text_orientation = text_orientation)
    
    
    def draw_curve(self, points, line_color="black", line_weight=1):
        im = self.image
        
        line_color = self.translate_color(line_color);
        font_color = line_color
        im.set_source_rgb(line_color[0], line_color[1], line_color[2]);
        im.set_line_width(line_weight);

        graph_data = points

        prepared_data = [];

        for i in range(0, len(graph_data)):
            x = graph_data[i][0];
            y = graph_data[i][1];

            #print "x = $x, y = $y\n";

            if((i != 0) and (i != (len(graph_data) - 1))):
                (x_left, y_left) = (graph_data[i - 1][0], graph_data[i - 1][1]);
                (x_right, y_right) = (graph_data[i + 1][0], graph_data[i + 1][1]);
                step_x_left = (x - x_left) / 2;
                step_x_right = (x_right - x) / 2;
                (dx, dy) = (x_right - x_left, y_right - y_left);
                h = 2*math.sqrt(dx*dx + dy*dy);

                if(h == 0):
                    (cx1, cy1, cx2, cy2) = (x, y, x, y)
                else:
                    (dx1, dy1) = ((dx * step_x_left) / h, (dy * step_x_left) / h);
                    (dx2, dy2) = ((dx * step_x_right) / h, (dy * step_x_right) / h);
                    (cx1, cx2) = (x - dx1, x + dx2);
                    (cy1, cy2) = (y - dy1, y + dy2);
            else:
                (cx1, cy1, cx2, cy2) = (x, y, x, y)

            #print "Adding point\n";
            point = (x, y, cx1, cy1, cx2, cy2)
            prepared_data.append(point)


        for i in range(0, len(prepared_data)-1):
            #print "i = $i\n";
            (x, y)     = (prepared_data[i][0], prepared_data[i][1])
            (cx1, cy1) = (prepared_data[i][4], prepared_data[i][5])
            (cx2, cy2) = (prepared_data[i + 1][2], prepared_data[i + 1][3])
            (x2, y2) = (prepared_data[i + 1][0], prepared_data[i + 1][1])
            im.move_to(x, y)
            #print "cx1=$cx1,cy1=$cy1,cx2=$cx2,cy2=$cy2,x2=$x2,y2=$y2\n";


            im.curve_to(cx1, cy1, cx2, cy2, x2, y2)

        im.stroke()
        
    def draw_arrow_head(self,x,y,angle,arrow_type=2,arrow_size=2,arrow_color="#000000"):

        arrow_color = self.translate_color(arrow_color)
        
        alpha = 90 + angle
        beta = 90 - angle
        
        if(arrow_type == 2):
            print "Do I get here?"
            self.image.new_path();
            xoff = 4 * (arrow_size) * math.sin((beta-35)/57.2957795);
            yoff = 4 * (arrow_size) * math.cos((beta-35)/57.2957795);
            
            self.image.move_to(x, y);
            self.image.line_to(x + xoff, y + yoff);
                
            xoff = 4 * (arrow_size) * math.cos((alpha-35)/57.2957795);
            yoff = 4 * (arrow_size) * math.sin((alpha-35)/57.2957795);
            
            self.image.line_to(x + xoff, y + yoff);
            self.image.line_to(x, y);
            
            self.image.set_source_rgb(arrow_color[0], arrow_color[1], arrow_color[2]);
            self.image.fill_preserve();
            self.image.stroke();
            
    def draw_line(self, x1, y1, x2, y2, text="", line_color="black", background_color="white", line_weight=1, line_pattern=1):
        
        line_color = self.translate_color(line_color)
        font_color = self.translate_color(background_color)

        id = 0
    
        arrow_begin = 0
        arrow_begin_size = 1
        arrow_begin_color = line_color
        arrow_end = 0
        arrow_end_size = 1
        
        if(line_pattern == 1):
            a = cairo_access.new_doubleArray(2)
            cairo_access.doubleArray_setitem(a, 0, 1)
            cairo_access.doubleArray_setitem(a, 1, 1)
            self.image.set_dash(a, 2, 0.0)
            cairo_access.delete_doubleArray(a)
        elif(line_pattern == 2):
            a = cairo_access.new_doubleArray(2);
            cairo_access.doubleArray_setitem(a, 0, 2);
            cairo_access.doubleArray_setitem(a, 1, 2);
            self.image.set_dash(a, 2, 0.0);
            cairo_access.delete_doubleArray(a);
       
        elif(line_pattern == 3):
            a = cairo_access.new_doubleArray(2);
            cairo_access.doubleArray_setitem(a, 0, 3);
            cairo_access.doubleArray_setitem(a, 1, 3);
            self.image.set_dash(a, 2, 0.0);
            cairo_access.delete_doubleArray(a);

        elif(line_pattern == 4):
            a = cairo_access.new_doubleArray(2);
            cairo_access.doubleArray_setitem(a, 0, 4);
            cairo_access.doubleArray_setitem(a, 1, 4);
            self.image.set_dash(a, 2, 0.0);
            cairo_access.delete_doubleArray(a);

        # Now calculate the position of any arrows if it is necessary
        # to display them.
        x = x2 - x1;
        y = y2 - y1;
        z = math.sqrt(abs(x*x) + abs(y*y));
        
        # The 57.2957795 is used to convert radians to degrees
        alpha = math.asin(y/z) * 57.2957795;
        beta = 90 - alpha;
        
        if(x1 > x2):
            tmp = x1
            x1 = x2
            x2 = x1;
            beta = -beta;
            alpha = 360 - alpha;
        
        if(y1 > y2):
            tmp = y1;
            y1 = y2;
            y2 = y1;
        
        self.image.move_to(x1, y1)
        
        self.image.set_source_rgb(line_color[0], line_color[1], line_color[2])
        
        self.image.set_line_width(line_weight)
        self.image.line_to(x2, y2)
        
        self.image.stroke()
        
        # Now clear the dash pattern
        a = cairo_access.new_doubleArray(2);
        cairo_access.doubleArray_setitem(a, 0, 0);
        cairo_access.doubleArray_setitem(a, 1, 0);
        self.image.set_dash(a, 0, 0.0);
        cairo_access.delete_doubleArray(a);
        
        if(arrow_begin):
            self.draw_arrow_head(x = x1, y = y1, angle = 360-beta,
                                arrow_type = arrow_begin,
                                arrow_size = arrow_begin_size,
                                arrow_color = arrow_begin_color)

        #
        #if($propsRef->{"arrow-end"} > 0)
        #{
        #    $self->drawArrowHead({"x" => $propsRef->{"x2"},
        #                          "y" => $propsRef->{"y2"},
        #                          "arrow-type" => $propsRef->{"arrow-end"},
        #                          "angle" => 180 - $beta,
        #                          "arrow-size" => $propsRef->{"arrow-end-size"},
        #                          "arrow-color" => $propsRef->{"arrow-end-color"}});
        #}

#=pod    
#
#        if($propsRef->{"text"} ne "")
#        {
#           $self->drawText({"x" => $propsRef->{"x1"} + $x/2,
#                            "y" => $propsRef->{"y1"} + $y/2,
#                            "text" => $propsRef->{"text"},
#                            "font-color" => $propsRef->{"font-color"},
#                            "angle" => $alpha,
#                            "font-size" => $propsRef->{"font-size"}});
#        }
#=cut    

        return id

    def draw_rounded_rect(self, x, y, width, height, radius, background_color, line_color):
        
        im = self.image
        
        #defaultProperty($propsRef, "line-color", "#000000");
        #defaultProperty($propsRef, "background-color", "#FFFFFF")
        background_color = self.translate_color(background_color)
        line_color = self.translate_color(line_color)

        #/* a custom shape, that could be wrapped in a function */
        #radius = 5  #/*< and an approximate curvature radius */        
        x0       = x   #/*< parameters like cairo_rectangle */
        y0       = y
        rect_width  = width
        rect_height = height

        im.save()
        im.set_line_width(0.9)

        x1 = x0+rect_width
        y1 = y0+rect_height

        if(rect_width/2<radius):
            if(rect_height/2<radius):
                im.move_to  (x0, (y0 + y1)/2)
                im.curve_to (x0 ,y0, x0, y0, (x0 + x1)/2, y0)
                im.curve_to (x1, y0, x1, y0, x1, (y0 + y1)/2)
                im.curve_to (x1, y1, x1, y1, (x1 + x0)/2, y1)
                im.curve_to (x0, y1, x0, y1, x0, (y0 + y1)/2)
            else:
                im.move_to  (x0, y0 + radius)
                im.curve_to (x0 ,y0, x0, y0, (x0 + x1)/2, y0)
                im.curve_to (x1, y0, x1, y0, x1, y0 + radius)
                im.line_to (x1 , y1 - radius)
                im.curve_to (x1, y1, x1, y1, (x1 + x0)/2, y1)
                im.curve_to (x0, y1, x0, y1, x0, y1- radius)
        else:
            if(rect_height/2<radius):
                im.move_to  (x0, (y0 + y1)/2)
                im.curve_to (x0 , y0, x0 , y0, x0 + radius, y0)
                im.line_to (x1 - radius, y0)
                im.curve_to (x1, y0, x1, y0, x1, (y0 + y1)/2)
                im.curve_to (x1, y1, x1, y1, x1 - radius, y1)
                im.line_to (x0 + radius, y1)
                im.curve_to (x0, y1, x0, y1, x0, (y0 + y1)/2)
            else:
                im.move_to  (x0, y0 + radius)
                im.curve_to (x0 , y0, x0 , y0, x0 + radius, y0)
                im.line_to (x1 - radius, y0)
                im.curve_to (x1, y0, x1, y0, x1, y0 + radius)
                im.line_to (x1 , y1 - radius)
                im.curve_to (x1, y1, x1, y1, x1 - radius, y1)
                im.line_to (x0 + radius, y1)
                im.curve_to (x0, y1, x0, y1, x0, y1- radius)
        im.close_path()
        
        im.set_source_rgb(background_color[0], background_color[1], background_color[2])
        im.fill_preserve()
        im.set_source_rgb(line_color[0], line_color[1], line_color[2])
        im.stroke()

        im.restore()

    def translate_color(self, color):

        if(isinstance(color, (list,tuple))):
            return color

        color = color.upper()
        color_array = []
        
        if(color == "BLUE"):
            color_array = (0,0,1)
        elif(color == "RED"):
            color_array = (1,0,0)
        elif(color == "GREEN"):
            color_array = (0,1,0)
        elif(color == "PURPLE"):
            color_array = (0x99/256.0, 0x66/256.0,1)
        elif(color == "BLACK"):
            color_array = (0,0,0)
        elif(color == "WHITE"):
            color_array = (1,1,1)
        else:
           
            expr = re.compile("([0-9A-F]{2})([0-9A-F]{2})([0-9A-F]{2})")
            matches = expr.search(color)

            if(matches != None):
                r = int(matches.groups()[0], 16)
                g = int(matches.groups()[1], 16)
                b = int(matches.groups()[2], 16)
                color_array = (r/256.0,
                               g/256.0,
                               b/256.0)
            else:
                color_array = (0,0,0)
        
        return color_array




class graph_t():

    def __init__(self, width, height):
        self.width  = width - 280
        self.height = height - 110
        
        self.left = 100
        self.right = self.width + self.left
        self.top = 50
        self.bottom = self.top + self.height
        self.title = ""
        self.subtitle    = ""
        self.cindex  = 0
        
        self.datasets = {}
        self.xaxis = {}
        self.yaxis = {}

        self.graph = cairo_t(self.width + 280, self.height + 110)
        

    def add_data_set(self, dataset, name, color=None):
    
        colors = []
        colors.append("#FF0000")
        colors.append("#00FF00")
        colors.append("#0000FF")
        colors.append("#FF00FF")
        colors.append("#FFFF00")
        colors.append("#00FFFF")
        colors.append("#22FF98")
        colors.append("#008080") # teal
        colors.append("#8B4513") # saddlebrown
        colors.append("#800080") # purple
        colors.append("#DBBFD8") # thistle
        colors.append("#0000CD") # mediumblue
        colors.append("#3CB371") # medimuseagreen
        colors.append("#90EE90") # lightgreen
        colors.append("#FF8C00") # darkorange
        colors.append("#9ACD32") # yellowgreen
        colors.append("#000000") # black
        colors.append("#7FFF00") # chartreuse
        colors.append("#4B0082") # indigo
        colors.append("#DA70D6") # orchid
        colors.append("#D5FF45")
        colors.append("#FFB26E")
        colors.append("#FFA4C4")
        colors.append("#DD0070")
        colors.append("#D80017")
        colors.append("#3E008C")
        colors.append("#666EFF")
        colors.append("#88D7FF")
        colors.append("#FF0000")
        colors.append("#00FF00")
        colors.append("#0000FF")
    
        cindex = self.cindex
    
        if(color != None):
            color = colors[cindex]
            cindex+=1
            self.cindex = cindex
        
        self.datasets[name] = {}
        self.datasets[name]["color"] = color
        self.datasets[name]["data"] = {}
        
        for element in dataset:
            self.datasets[name]["data"][element] = dataset[element]


    def get_max_xcoordiate(self):
        maxX = 0
        
        for dataset in self.datasets:
            for key in self.datasets[dataset]["data"]:
                if(key > maxX):
                    maxX = key
        
        #if(1 == $self->{XAXIS}{"autoscale"})
        #{
        #   $maxX = (ceil($maxX / 10.0))*10;
        #}
        
        return maxX


    def get_max_ycoordinate(self):
        maxY = 0;
        
        for dataset in self.datasets:
            for key in self.datasets[dataset]["data"]:
                value = self.datasets[dataset]["data"][key]
                
                if(value > maxY):
                    maxY = value
    
        if(maxY < 0.01):
            maxY = 0.01
        elif(maxY < 0.1):
            maxY = 0.1
        elif(maxY < 1):
            maxY = 0.1
        elif(maxY < 10):
            pass
        else:
            maxY = (ceil(maxY/ 10.0))*11
    
        if(maxY < self.yaxis["max"]):
            maxY = self.yaxis["max"]
        
        return maxY


    def set_xaxis(self, label, color, min, max, increment):
       
        self.xaxis["label"]     = label
        self.xaxis["min"]       = min
        self.xaxis["max"]       = max
        self.xaxis["increment"] = increment
        self.xaxis["color"]     = color
        self.xaxis["autoscale"] = 1


    def set_yaxis(self, label, color, min, max, increment):
        self.yaxis["label"]     = label
        self.yaxis["min"]       = min
        self.yaxis["max"]       = max
        self.yaxis["increment"] = increment
        self.yaxis["color"]     = color

    def set_title(self, title, subtitle):
        self.title = title
        self.subtitle = subtitle

    def draw_legend(self):
       graph = self.graph
       
       top = self.top
       left = self.left
       right = self.right
       y = top + 50
          
       graph.draw_text(x = right + 10,
                       y = y,
                       font_color = "#000000",
                       text       = "Legend")
       y += 24
     
       #for dataset (sort {$a cmp $b}  keys(%{$self->{DATASETS}}))
       for dataset in self.datasets:
           color = self.datasets[dataset]["color"]
       
           graph.draw_rect(
               x = right + 15,
               y = y,
               width = 20,
               height = 20,
               background_color = color,
               line_color = color)
           
           graph.draw_text(
               x = right + 40,
               y = y+2,
               font_size = 8,
               font_color = color,
               text       = dataset)
           y += 24      


    def draw_title(self):
        graph = self.graph
       
        left = self.left
        right = self.right
        top = self.top
        y = top - 36
          
        graph.draw_text(x = left + ((right - left)/2),
                        y = y,
                        font_color = "#000000",
                        text       = self.title,
                        text_anchor = "middle",
                        font_size   = 16)
    
        subtitle = self.subtitle

        if(subtitle != None):
            graph.draw_text(
                x = left + ((right - left)/2),
                y = y + 20,
                font_color = "#000000",
                text       = subtitle,
                text_anchor = "middle",
                font_size   = 10)

    def draw_values(self):
        return 0


    def draw_graph(self):
       graph = self.graph
       
       left   = self.left
       top    = self.top
       width  = self.width
       height = self.height

       #print "left: %d" % left
       #print "top: %d" % top
       #print "width: %d" % width
       #print "height: %d" % height

       padding=10
       
       graph.draw_rounded_rect(
           x = padding,
           y = padding,
           width = width + 280 - (2*padding),
           height = height + 110 - (2*padding),
           radius = 10,
           background_color = "#C0C0C0",
           line_color = "#C0C0C0")
       
       padding+=1
       graph.draw_rounded_rect(
           x = padding,
           y = padding,
           width = width + 280 - (2*padding),
           height = height + 110 - (2*padding),
           radius = 10,
           background_color = "#f0f0f0",
           line_color = "#C0C0C0")
       
       graph.draw_rounded_rect(
           x = left,
           y = top,
           width = width,
           height = height,
           radius = 10,
           background_color = "#FFFFFF",
           line_color = "#000000")
    
