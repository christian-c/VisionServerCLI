# -*- coding: utf-8 -*-
import time
import math
import datetime

# for socket connection
import re
import socket
import threading
import thread
import cmd
host = ''
port = 22222

smin = 0.9
smax = 1.1
amin = -3.14
amax = 6.28
cam_id = 3
##### Check components ######

############################

class CmdControl(cmd.Cmd):
    use_rawinput = False 

    def __init__(self,addr='0.0.0.0',port=22222,timeout=0.1):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        self.socket.connect((addr,port))
        self.socket.settimeout(timeout)
        cmd.Cmd.__init__(self) 

    prompt = "[vision] "

    def do_init(self,line):
      msg = 'OpenCamera ' + str(cam_id) + ' uEye ' + str(cam_id) 
      msg += ' CamParams/CamParam_Interior_Raw_' + str(cam_id) + '.campar'
      self.socket.send(msg)
    def do_capture(self,line):
      msg = 'GrabImage ' + str(cam_id)
      self.socket.send(msg)

    def do_setcam(self,line):
      global cam_id
      t = line.split(" ")
      cam_id = t[0]

    def do_hsv_region(self, line):
      t = line.split(" ")
      if len(t) == 4:
        cx = t[0]
        cy = t[1]
        rl = t[2]
        rw = t[3]
        msg = 'CreateModel '+str(cam_id)+' HSVColorFilter 10 Rectangle,' + cx + ',' + cy + ',' + rl + ',' + rw
        self.socket.send(msg)
      else:
        print"Syntax error: hsv_rect <center_x> <center_y> <rect_l> <rect_w>"
        return

    def do_hsv_check(self,line): 
      msg = 'CreateModel ' + str(cam_id) + ' HSVColorFilter 40 '
      self.socket.send(msg)

    def do_hsv_filter(self,line):
      t = line.split(" ")
      if len(t) == 1:
        obj_id = t[0]

        msg = 'RunOnce HSVColorFilter ' + obj_id +' ' + str(cam_id)
        self.socket.send(msg)
      else:
        print"Syntax error: hsv_filter <Object ID>"
        return

    def do_hsv_param_save(self,line):
      msg = 'CreateModel ' + str(cam_id) + ' HSVColorFilter 20 '
      self.socket.send(msg)

    def do_setmodelparams(self,line):
      global smin, smax, amin, amax
      t = line.split(" ")
      if len(t) == 4:
        smin = float(t[0])
        smax = float(t[1])
        amin = float(t[2])
        amax = float(t[3])
      else:
        print"Syntax error: setmodelparams <ScaleMin> <ScaleMax>"
        print"                             <Anglestart> <AngleExtent"
        return        

    def do_getmodelparams(self,line):
      print "[scale_min, scale_max, angle_start, angle_extent = [%7.4f, %7.4f, %7.4f, %7.4f]" %(smin,smax,amin,amax)
    
    def do_createregion(self,line):
      t = line.split(" ")
      if len(t) == 5:
        shp = t[0]
        cx = t[1]
        cy = t[2]
        l1 = t[3]
        l2 = t[4]
        msg = 'CreateModel '+ str(cam_id) +' MatchScaledShape 10 Reset,Shape,'
        msg += str(smin)+','+str(smax)+','+str(amin)+','+str(amax)
        msg += ','+shp+','+cx+','+cy+','+l1+','+l2
        self.socket.send(msg)
      else:
        print "createregion <Shape> <CenterX> <CenterY> <Len1> <Len2> "    
        return

    def do_addregion(self,line):
      t = line.split(" ")
      if len(t) == 5:
        shp = t[0]
        cx = t[1]
        cy = t[2]
        l1 = t[3]
        l2 = t[4]
        msg = 'CreateModel ' +str(cam_id) + ' MatchScaledShape 10 Add,Shape,'
        msg += str(smin)+','+str(smax)+','+str(amin)+','+str(amax)
        msg += ','+shp+','+cx+','+cy+','+l1+','+l2
        self.socket.send(msg)
      else:
        print "addregion <Shape> <CenterX> <CenterY> <Len1> <Len2> "    
        return

    def do_subregion(self,line):
      t = line.split(" ")
      if len(t) == 5:
        shp = t[0]
        cx = t[1]
        cy = t[2]
        l1 = t[3]
        l2 = t[4]
        msg = 'CreateModel ' +str(cam_id)+' MatchScaledShape 10 Sub,Shape,'
        msg += str(smin)+','+str(smax)+','+str(amin)+','+str(amax)
        msg += ','+shp+','+cx+','+cy+','+l1+','+l2
        self.socket.send(msg)
      else:
        print "subregion <Shape> <CenterX> <CenterY> <Len1> <Len2> "    
        return

    def do_savemodel(self,line):
      t = line.split(" ")
      if len(t) == 2:
        m_name = t[0]
        typ = t[1]

        msg = 'CreateModel ' + str(cam_id) + ' MatchScaledShape 20 '+m_name+','
        msg += typ+','+str(smin)+','+str(smax)+','+str(amin)+','+str(amax)
        self.socket.send(msg)
        time.sleep(1)
        self.socket.send(b'LoadPlugins plugin')
      else:
        print "savemodel <ModelName> <Edge/Shape> "
        return

    def do_loadmodel(self,line):
      t = line.split(" ")
      if len(t) == 1:
        m_name = t[0]

        msg = 'CreateModel ' + str(cam_id)+ ' MatchScaledShape 30 '+m_name
        self.socket.send(msg)
      else:
        print "loadmodel <ModelName> "
        return
    
    def do_matchmodel(self,line):
      t = line.split(" ")
      if len(t) == 1:
        m_name = t[0]

        msg = 'RunOnce MatchScaledShape '+m_name+' ' + str(cam_id)
        self.socket.send(msg)
      else:
        print "  matchmodel <ModelName> "
        return
    def do_cmd_list(self,line):
      print "###################################################################"
      print "                  Vision Server CLI Command List                   "
      print "-------------------------------------------------------------------"
      print "-------------------------------------------------------------------"
      print "                              Basic                                "
      print "-------------------------------------------------------------------"
      print "  init                                                             "
      print "  setcam <CameraID>                                                "
      print "  capture                                                          "   
      print "-------------------------------------------------------------------"
      print "                         HSV Color Filter                          "
      print "-------------------------------------------------------------------"
      print "  hsv_region <CenterX> <CenterY> <RectL> <RectW>                   "
      print "  hsv_check                                                        "
      print "  hsv_param_save                                                   "
      print "  hsv_filter <ObjectID>                                            "
      print "-------------------------------------------------------------------"
      print "                          Shape Matching                           "
      print "-------------------------------------------------------------------"
      print "  getmodelparams                                                   "
      print "  setmodel params <ScaleMin> <ScaleMax> <AngleStart> <AngleExtent> "
      print "  createregion <Shape> <CenterX> <CenterY> <Len1> <Len2>           "    
      print "  addregion    <Shape> <CenterX> <CenterY> <Len1> <Len2>           "    
      print "  subregion    <Shape> <CenterX> <CenterY> <Len1> <Len2>           "    
      print "  savemodel <ModelName> <Edge/Shape>                               "
      print "  loadmodel <ModelName>                                            "
      print "  matchmodel <ModelName>                                           "
      print "###################################################################"

    def do_quit(self,line):
      self.socket.send(b'quit')
      return True


if __name__=='__main__':

    CmdControl().cmdloop()



