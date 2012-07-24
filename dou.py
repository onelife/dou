"""<title>DOU app, embedded software development and testing toolkit</title>

"""

# load pygame
import pygame
from pygame.locals import *
# load pgu
from pgu import gui
# load pyserial
from serial import *
from serial.tools.list_ports import comports
# load others
import thread
from threading import *
import time
from collections import deque
import sys ,os

# protocol
dou_id = {'start':0x5ad0, 'end':0xd0a5}
dou_header = {'cmd':0xd1, 'data':0xd2}
dou_command = {'none':'0',
               'init':'1',
               'clear':'2',
               'rdPoint':'3',
               'dwPoint':'4',
               'dwHCLine':'5', 
               'dwHLine':'6',
               'dwVLine':'7'}
dou_protocol = {'id':dou_id, 'header':dou_header, 'command':dou_command}

# app setting
screen = {'width':800, 'height':600}
msg_box = {'high':100, 'length':50, 'count':5}
dou_gui = {'screen':screen, 'msg_box':msg_box, 'spacer':8}


class PortDialog(gui.Dialog):
    def __init__(self,**params):
        title = gui.Label("Port setting")
        space = title.style.font.size(" ")
        
        self.serial_sel = gui.Select()
        for comport in reversed(list(comports())):
#        for comport in comports():
            self.serial_sel.add(comport[1],comport[0])
            if not self.serial_sel.value:
                self.serial_sel.value = comport[0]

        self.speed_sel = gui.Select(115200)
        self.speed_sel.add('115200',115200)
        self.speed_sel.add('57600',57600)
        self.speed_sel.add('38400',38400)
        self.speed_sel.add('19200',19200)
        # TODO!!!
        self.test2 = gui.ScrollArea(self.serial_sel.options,height=300)

        self.data_sel = gui.Select(EIGHTBITS)
        self.data_sel.add('8 bits',EIGHTBITS)
        self.data_sel.add('7 bits',SEVENBITS)

        self.parity_sel = gui.Select(PARITY_NONE)
        self.parity_sel.add('None',PARITY_NONE)
        self.parity_sel.add('Even',PARITY_EVEN)
        self.parity_sel.add('Odd',PARITY_ODD)

        self.stop_sel = gui.Select(STOPBITS_ONE)
        self.stop_sel.add('1 bits',STOPBITS_ONE)
        self.stop_sel.add('2 bits',STOPBITS_TWO)

        self.flow_sel = gui.Group(value=[])

        # table
        t = gui.Table()
        
        t.tr()
        t.td(gui.Label("Port: "),colspan=2,align=1)
        t.td(self.serial_sel,colspan=6,align=-1)

        t.tr()
        t.td(gui.Label("Baud Rate: "),colspan=2,align=1)
        t.td(self.speed_sel,colspan=6,align=-1)

        t.tr()
        t.td(gui.Label("Data Size: "),colspan=2,align=1)
        t.td(self.data_sel,colspan=6,align=-1)

        t.tr()
        t.td(gui.Label("Parity: "),colspan=2,align=1)
        t.td(self.parity_sel,colspan=6,align=-1)

        t.tr()
        t.td(gui.Label("Stop Bits: "),colspan=2,align=1)
        t.td(self.stop_sel,colspan=6,align=-1)

        t.tr()
        t.td(gui.Label("Flow Control: "),colspan=2,align=1)
        t.td(gui.Label("   Xon/Xoff"),align=1)
        t.td(gui.Checkbox(self.flow_sel,value='xonxoff'),align=-1)
        t.td(gui.Label("   RTS/CTS"),align=1)
        t.td(gui.Checkbox(self.flow_sel,value='rtscts'),align=-1)
        t.td(gui.Label("   DSR/DTR"),align=1)
        t.td(gui.Checkbox(self.flow_sel,value='dsrdtr'),align=-1)

        t.tr()
        e = gui.Button("Set")
        e.connect(gui.CLICK,self.send,gui.CHANGE)
        t.td(e,colspan=4)
        
        e = gui.Button("Cancel")
        e.connect(gui.CLICK,self.close,None)
        t.td(e,colspan=4)
        
        gui.Dialog.__init__(self,title,t)


##Documents layout widgets like words and images in a HTML document.  This
##example also demonstrates the ScrollBox container widget.
##::
class AboutDialog(gui.Dialog):
    def __init__(self,**params):
        title = gui.Label("About Cuzco's Paint")
        
        width = 400
        height = 200
        doc = gui.Document(width=width)
        
        space = title.style.font.size(" ")
        
        doc.block(align=0)
        for word in """DOU v0.1 by onelife""".split(" "): 
            doc.add(gui.Label(word))
            doc.space(space)
        doc.br(space[1])
        
        doc.block(align=-1)
        doc.add(gui.Image("dou.png"),align=1)
        for word in """I want to build this software as a embedded software development and testing toolkit.  I hope you enjoy it!""".split(" "): 
            doc.add(gui.Label(word))
            doc.space(space)
        doc.br(space[1])
        
        doc.block(align=-1)
        for word in """Why this software is named "DOU"?  DOU DOU is the nickname of my lovely baby daughter.  Yes, the photo displayed is my little princess.""".split(" "): 
            doc.add(gui.Label(word))
            doc.space(space)
        doc.br(space[1])


        gui.Dialog.__init__(self,title,gui.ScrollArea(doc,width,height))
##


class HelpDialog(gui.Dialog):
    def __init__(self,**params):
        title = gui.Label("Help")
        
        doc = gui.Document(width=400)
        
        space = title.style.font.size(" ")
        
        doc.block(align=-1)
        doc.add(gui.Image("dou.png"),align=1)
        for word in """DOU is a Python software based on pygame and pgu modules.""".split(" "): 
            doc.add(gui.Label(word))
            doc.space(space)
        doc.br(space[1])
        
        gui.Dialog.__init__(self,title,doc)
        
class QuitDialog(gui.Dialog):
    def __init__(self,**params):
        title = gui.Label("Quit")
        
        t = gui.Table()
        
        t.tr()
        t.add(gui.Label("Are you sure you want to quit?"),colspan=2)
        
        t.tr()
        e = gui.Button("Okay")
        e.connect(gui.CLICK,self.send,gui.QUIT)
        t.td(e)
        
        e = gui.Button("Cancel")
        e.connect(gui.CLICK,self.close,None)
        t.td(e)
        
        gui.Dialog.__init__(self,title,t)

class WelcomeDialog(gui.Dialog):
    def __init__(self,**params):
        title = gui.Label("Welcome")
        
        doc = gui.Document(width=400)
        
        space = title.style.font.size(" ")

        doc.block(align=-1)
        doc.add(gui.Image("dou.png"),align=1)
        for word in """Welcome to DOU. DOU is a embedded software development and testing toolkit.""".split(" "): 
            doc.add(gui.Label(word))
            doc.space(space)

        gui.Dialog.__init__(self,title,doc)


class OpenDialog(gui.Dialog):
    def __init__(self,**params):
        title = gui.Label("Open Picture")
        
        t = gui.Table()
        
        self.value = gui.Form()
        
        t.tr()
        t.td(gui.Label("Open: "))
        t.td(gui.Input(name="fname"),colspan=3)
        
        t.tr()
        e = gui.Button("Okay")
        e.connect(gui.CLICK,self.send,gui.CHANGE)
        t.td(e,colspan=2)
        
        e = gui.Button("Cancel")
        e.connect(gui.CLICK,self.close,None)
        t.td(e,colspan=2)
        
        gui.Dialog.__init__(self,title,t)

class SaveDialog(gui.Dialog):
    def __init__(self,**params):
        title = gui.Label("Save As...")
        
        t = gui.Table()
        
        self.value = gui.Form()
        
        t.tr()
        t.td(gui.Label("Save: "))
        t.td(gui.Input(name="fname"),colspan=3)
        
        t.tr()
        e = gui.Button("Okay")
        e.connect(gui.CLICK,self.send,gui.CHANGE)
        t.td(e,colspan=2)
        
        e = gui.Button("Cancel")
        e.connect(gui.CLICK,self.close,None)
        t.td(e,colspan=2)
        
        gui.Dialog.__init__(self,title,t)


class DouLcd(gui.Widget):
    def __init__(self, command, messages, log, **params):
        gui.Widget.__init__(self, **params)    
        # lcd drawing thread
        self.lcd_thread = Lcd(command, messages, log)
        self.lcd_thread.start()

    def event(self, e):
        if not self.lcd_thread.surface:
            return
        
 #       if e.type == gui.MOUSEBUTTONDOWN:
 #           if hasattr(self,app.mode.value+"_down"):
 #               action = getattr(self,app.mode.value+"_down")
 #               action(e)
 #       if e.type == gui.MOUSEMOTION:
 #           if hasattr(self,app.mode.value+"_motion"):
 #               action = getattr(self,app.mode.value+"_motion")
 #               action(e)
 #       if e.type is gui.MOUSEBUTTONUP:
 #           if hasattr(self,app.mode.value+"_up"):
 #               action = getattr(self,app.mode.value+"_up")
 #               action(e)
    
    ##The Painter class has its own paint method to render the painting surface and overlay.
    ##::
    def paint(self, s):
        if self.lcd_thread.surface:
            s.blit(self.lcd_thread.surface, (0, 0))
    ##


class DouMessage(gui.ScrollArea):
    def __init__(self, messages, width, height, **params):
        self.messages = messages
        self.count = 0
        self.value = 0
        self.updating = False
        self.table = gui.Table()
        gui.ScrollArea.__init__(self, widget = self.table,
                                width = width, height = height,
                                hscrollbar = False, step = 5,
                                **params)

    def _vscrollbar_changed(self, xxx):
        if self.vscrollbar.value > self.vscrollbar.max:
            self.vscrollbar.value = self.vscrollbar.max
            return

        self.value = self.vscrollbar.value
        if self.updating or not (self.count > dou_gui['msg_box']['length']):
            self.updating = False
            self.sbox.offset[1] = int(round(float(min(self.count, dou_gui['msg_box']['length'])) /
                                            dou_gui['msg_box']['length'] * (self.widget.rect.h - self.sbox.style.height)))

        else:
            print 'self.value %d, value %d, count %d, offset %d' % (self.value, self.vscrollbar.value, self.count, self.sbox.offset[1])
            index = max(0, self.vscrollbar.value - (dou_gui['msg_box']['length'] + 1 / 2))
            load_index = index = min(index, self.count - dou_gui['msg_box']['length'])
            
            # reload messages
            self.table.clear()
            for _ in xrange(dou_gui['msg_box']['length']):
                message = self.messages[index]
                index += 1
                self.table.tr()
                self.table.td(gui.Label(message), align = -1)

            self.sbox.offset[1] = int(round(float(self.vscrollbar.value - load_index) /
                                            dou_gui['msg_box']['length'] * (self.widget.rect.h - self.sbox.style.height)))

            print 'load %d, self.value %d, value %d, count %d, offset %d' % (load_index, self.value, self.vscrollbar.value, self.count, self.sbox.offset[1])

        self.sbox.reupdate()

    def paint(self, s):
        total = len(self.messages)
        if total == self.count:
            pass
        
        else:
            self.updating = True
            if total > dou_gui['msg_box']['length']:
                # prepare to reload messages
                length = dou_gui['msg_box']['length']
                index = total - dou_gui['msg_box']['length']
                self.table.clear()

            else:
                # prepare to add messages
                length = total - self.count
                index = self.count

            self.count = total
            for _ in xrange(length):
                message = self.messages[index]
                index += 1
                self.table.tr()
                self.table.td(gui.Label(message), align = -1)

            self.resize()
            #self.table.resize()
            self.vscrollbar.value = self.vscrollbar.max
            
        #super(DouMessage, self).paint(s)
        gui.ScrollArea.paint(self, s)

    # hack resize()
    def resize(self,width=None,height=None):
        widget = self.widget
        box = self.sbox
        
        #self.clear()
        #table.Table.clear(self)
        gui.Table.clear(self)
        #print 'resize',self,self._rows
        
        self.tr()
        self.td(box)
        
        widget.rect.w, widget.rect.h = widget.resize()
        my_width,my_height = self.style.width,self.style.height
        if not my_width:
            my_width = widget.rect.w
            self.hscrollbar = False
        if not my_height:
            my_height = widget.rect.h
            self.vscrollbar = False
        
        box.style.width,box.style.height = my_width,my_height #self.style.width,self.style.height
        
        box.rect.w,box.rect.h = box.resize()
        
        #print widget.rect
        #print box.rect
        #r = table.Table.resize(self,width,height)
        #print r
        #return r
        
        #print box.offset
        
#         #this old code automatically adds in a scrollbar if needed
#         #but it doesn't always work
#         self.vscrollbar = None
#         if widget.rect.h > box.rect.h:
#             self.vscrollbar = slider.VScrollBar(box.offset[1],0, 65535, 0,step=self.step) 
#             self.td(self.vscrollbar)
#             self.vscrollbar.connect(CHANGE, self._vscrollbar_changed, None)
#             
#             vs = self.vscrollbar
#             vs.rect.w,vs.rect.h = vs.resize()
#             box.style.width = self.style.width - vs.rect.w
#             
#             
#         self.hscrollbar = None
#         if widget.rect.w > box.rect.w:
#             self.hscrollbar = slider.HScrollBar(box.offset[0], 0,65535, 0,step=self.step)
#             self.hscrollbar.connect(CHANGE, self._hscrollbar_changed, None)
#             self.tr()
#             self.td(self.hscrollbar)
#             
#             hs = self.hscrollbar
#             hs.rect.w,hs.rect.h = hs.resize()
#             box.style.height = self.style.height - hs.rect.h

        xt,xr,xb,xl  = gui.pguglobals.app.theme.getspacing(box)
        

        if self.vscrollbar:
            self.vscrollbar = gui.VScrollBar(self.value, 0, self.count, 0,step=self.step) 
            self.td(self.vscrollbar)
            self.vscrollbar.connect(gui.CHANGE, self._vscrollbar_changed, None)
            
            vs = self.vscrollbar
            vs.rect.w,vs.rect.h = vs.resize()
            if self.style.width:
                box.style.width = self.style.width - (vs.rect.w + xl+xr)

        if self.hscrollbar:
            self.hscrollbar = gui.HScrollBar(box.offset[0], 0,65535, 0,step=self.step)
            self.hscrollbar.connect(gui.CHANGE, self._hscrollbar_changed, None)
            self.tr()
            self.td(self.hscrollbar)
            
            hs = self.hscrollbar
            hs.rect.w,hs.rect.h = hs.resize()
            if self.style.height:
                box.style.height = self.style.height - (hs.rect.h + xt + xb)
            
        if self.hscrollbar:
            hs = self.hscrollbar
            hs.min = 0
            hs.max = widget.rect.w - box.style.width
            hs.style.width = box.style.width
            hs.size = hs.style.width * box.style.width / max(1,widget.rect.w)
        else:
            box.offset[0] = 0
            
        if self.vscrollbar:
            vs = self.vscrollbar
            #vs.min = 0
            vs.max = self.count
            vs.style.height = box.style.height
            vs.size = vs.style.height * box.style.height / max(1,widget.rect.h)
        else:
            box.offset[1] = 0
            
        #print self.style.width,box.style.width, hs.style.width

        #r = table.Table.resize(self,width,height)
        r = gui.Table.resize(self,width,height)
        return r


class App(gui.Desktop):
    def __init__(self, **params):
        gui.Desktop.__init__(self, **params)

        c = gui.Container(**dou_gui['screen'])
        
        self.fname = 'untitled.tga'

        # init
        self.command = {'buffer':list(), 'index':0}
        lcd_command = deque()
        self.dispatch = {'dou_lcd':lcd_command}
        self.messages = list()
        cmd_log = {'file':open("dou.log", "w"), 'token':thread.allocate_lock()}
        msg_log = {'file':open("msg.log", "w"), 'token':thread.allocate_lock()}
        self.log = {'cmd_log':cmd_log, 'msg_log':msg_log}

        # DOU message
 #       self.msg = DouMessage(messages = self.messages,
 #                             width = c.rect.w - spacer * 2,
 #                             height = dou_gui['msg_box']['high'],
 #                             style={'border':1})
 #       c.add(self.msg, spacer, c.rect.bottom - self.msg.rect.h - spacer)
        
        # command processing thread
        self.process_thread = Process(command = self.command, dispatch = self.dispatch,
                                      messages = self.messages, log = self.log)
        self.process_thread.start()


        # show welcome
        welcome_d = WelcomeDialog()
        self.connect(gui.INIT, welcome_d.open, None)
        
        self.port_d = PortDialog()
        welcome_d.connect(gui.CLOSE,self.port_d.open,None)
        self.port_d.connect(gui.CHANGE,self.action_port,None)

        self.open_d = OpenDialog()
        self.open_d.connect(gui.CHANGE,self.action_open,None)
        
        self.save_d = SaveDialog()
        self.save_d.connect(gui.CHANGE,self.action_saveas,None)
        
        self.quit_d = QuitDialog()
        self.quit_d.connect(gui.QUIT,self.action_quit,None)
        
        self.help_d = HelpDialog()
        self.about_d = AboutDialog()
        
        ##Initializing the Menus, we connect to a number of Dialog.open methods for each of the dialogs.
        ##::
        menus = gui.Menus([
            ('File/Open',self.open_d.open,None),
            ('File/Save',self.action_save,None),
            ('File/Save As',self.save_d.open,None),
            ('File/Exit',self.quit_d.open,None),
            ('Help/Help',self.help_d.open,None),
            ('Help/About',self.about_d.open,None),
            ])
        ##
        c.add(menus,0,0)
        menus.rect.w,menus.rect.h = menus.resize()
        #print 'menus',menus.rect
        
        ##We utilize a Toolbox.  The value of this widget determins how drawing is done in the Painter class.
        ##::
        self.mode = mode = gui.Toolbox([
            ('Tool1','tool1'),
            ('Tool2','tool2'),
            ('Tool3','tool3'),
            ('Tool4','tool4'),
            ],cols=1,value='draw')
        ##
        c.add(mode,0,menus.rect.bottom + dou_gui['spacer'])
        mode.rect.x,mode.rect.y = mode.style.x,mode.style.y
        mode.rect.w,mode.rect.h = mode.resize()
        
        # DOU display
        self.lcd = DouLcd(command = self.dispatch['dou_lcd'],
                          messages = self.messages,
                          log = self.log,
                          width = c.rect.w - mode.rect.w - dou_gui['spacer'] * 2,
                          #height = c.rect.h - menus.rect.h - self.msg.rect.h - spacer * 3,
                          height = c.rect.h - menus.rect.h - 100 - dou_gui['spacer'] * 3,
                          style={'border':1})
        c.add(self.lcd, mode.rect.w + dou_gui['spacer'], menus.rect.bottom + dou_gui['spacer'])
        #self.lcd.rect.w,self.lcd.rect.h = self.lcd.resize()

        self.widget = c
    
    def run(self, widget=None, screen=None, delay = 10):
        self.init(self.widget)
        rest = True

        while not self._quit:
            if len(self.command['buffer']) or len(self.messages):
                self.repaint()
                rest = False
         
            self.loop()
            if rest:
                pass
                pygame.time.wait(delay)

            else:
                rest = True
                
        # before exit
        app.quit_d.open()

    def event(self, e):
        if e.type is QUIT:
            app.quit_d.open()

        else:
            gui.Desktop.event(self, e)

    def paint(self,screen=None):
        gui.Desktop.paint(self, screen)

        if (screen):
            length = len(self.messages)
            if length > 0:
                font = pygame.font.SysFont("arial", 16);
                font_height = font.get_linesize()

                x = font.get_height()
                y = dou_gui['screen']['height'] - dou_gui['spacer'] - dou_gui['msg_box']['count'] * font_height
                if length > dou_gui['msg_box']['count']:
                    length = dou_gui['msg_box']['count']
                    
                for i in xrange(-1, -length - 1, -1):
                    if 'Error' in self.messages[i]:
                        color = (255, 0, 0)

                    else:
                        color = (0, 0, 0)
                        
                    self.screen.blit(font.render(self.messages[i][:150], True, color), (x, y))
                    y += font_height

            

    def action_port(self, value):
        self.port_d.close()
        config = {'port':self.port_d.serial_sel.value, \
                  'baudrate':self.port_d.speed_sel.value, \
                  'bytesize':self.port_d.data_sel.value, \
                  'parity':self.port_d.parity_sel.value, \
                  'stopbits':self.port_d.stop_sel.value}

        if self.port_d.flow_sel.value.count('xonxoff'):
            config['xonxoff'] = True

        if self.port_d.flow_sel.value.count('rtscts'):
            config['rtscts'] = True

        if self.port_d.flow_sel.value.count('dsrdtr'):
            config['dsrdtr'] = True

        config['timeout'] = 0
        
        print 'Serial Port Setting: %s' % str(config)
        self.port_thread = Port(config, self.command)
        self.port_thread.start()
     
    def action_save(self,value):
        pass
        #pygame.image.save(self.painter.surface,self.fname)
        
    def action_saveas(self,value):
        self.save_d.close()
        self.fname = self.save_d.value['fname'].value
        #pygame.image.save(self.painter.surface,self.fname)
        
    def action_open(self,value):
        self.open_d.close()
        self.fname = self.open_d.value['fname']
        #self.painter.surface = pygame.image.load(self.fname)
        #self.painter.repaint()
        
    def action_quit(self,value):
        if hasattr(self.lcd, 'lcd_thread'):
            self.lcd.lcd_thread.done = True;

        if hasattr(self, 'process_thread'):
            self.process_thread.done = True;

        if hasattr(self, 'message_thread'):
            self.message_thread.done = True;
        
        if hasattr(self, 'port_thread'):
            self.port_thread.done = True;

#        temp = open("msg.log", "w")
#        for msg in self.messages:
#            temp.write('%s\n' % msg)
#        temp.close()

        self.log['msg_log']['file'].close()
        self.log['cmd_log']['file'].close()
        
        print '[app] quit'
        pygame.quit()
        sys.exit()

        
class Port(Thread):
    """
    Serial port transceiver thread.
    
    """
    def __init__(self, config, command):
        Thread.__init__(self)

        self.done = False
        self.config = config
        self.command = command

    def loop(self, delay):
        if self.port.inWaiting():
            line = self.port.readline()
            self.command['buffer'].append(line)

        else:
            if len(self.command['buffer']) == self.command['index']:
                self.command['buffer'] = []
                self.command['index'] = 0

            time.sleep(float(delay) / 1000)

    def run(self, delay = 5):
        self.port = Serial(**self.config)
        self.port.flushInput()
        self.port.flushOutput()

        if not self.port.isOpen():
            self.port.open()

        while not self.done:
            self.loop(delay)

        # before exit
        self.port.close()
        print '[Port] quit\n'
        

class CommandError(Exception):
    def __init__(self, error, command):
        self.error = error
        self.command = command

    def __str__(self):
        return self.error + ': ' + self.command


class Process(Thread):
    """
    Command processing thread.
    
    """
    def __init__(self, command, dispatch, messages, log):
        Thread.__init__(self)

        self.done = False
        self.command = command
        self.dispatch = dispatch
        self.messages = messages
        self.log = log
        self.count = 0

    def loop(self, delay):
        if (len(self.command['buffer']) == 0) or (len(self.command['buffer']) == self.command['index']):
            time.sleep(float(delay) / 1000)
            return

        else:
            retry = 3
            try:
                # extract the command from raw input
                try:
                    line = self.command['buffer'][self.command['index']]
                except IndexError:
                    time.sleep(float(delay) / 1000)
                    return
                
                self.command['index'] += 1
                if (self.get_start(line[:2])):
                    command = line[2:]

                    while (not self.get_end(line[-3:-1])) and retry > 0:
                        try:
                            line = self.command['buffer'][self.command['index']]
                        except IndexError:
                            time.sleep(float(delay) / 1000)
                            return

                        self.command['index'] += 1
                        command = command + line
                        retry -= 1

                    command = command[:-3]
                    to_log = ''
                    for ch in command:
                        to_log += '%02x' % ord(ch)

                    # logging
                    self.log['cmd_log']['token'].acquire()
                    self.log['cmd_log']['file'].write('%08d' % self.count + ': ' + to_log + '\n')
                    self.log['cmd_log']['token'].release()
                    self.count += 1

                    # put in command queue
                    if retry <= 0:
                        raise CommandError('No ending', to_log)

                    # Currently, there is only LCD commands
                    self.dispatch['dou_lcd'].append(command)
        
            except (IndexError, CommandError) as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]      
                print(exc_type, fname, exc_tb.tb_lineno)

                print 'Process Error: %s' % str(e)
                self.messages.append('<Process Error: %s>' % str(e))
                self.log['msg_log']['token'].acquire()
                self.log['msg_log']['file'].write('<Process Error: %s>\n' % str(e))
                self.log['msg_log']['token'].release()

    def run(self, delay = 10):
        while not self.done:
            self.loop(delay)

        # before exit
        print 'Log command count: %d\n' % self.count

    def get_start(self, buffer):
        id = ord(buffer[0]) + (ord(buffer[1]) << 8)

        if (id == dou_protocol['id']['start']):
            return True

        else:
            return False

    def get_end(self, buffer):
        id = ord(buffer[0]) + (ord(buffer[1]) << 8)

        if (id == dou_protocol['id']['end']):
            return True

        else:
            return False


class Lcd(Thread):
    """
    LCD drawing thread.
    
    """
    def __init__(self, command, messages, log):
        Thread.__init__(self)

        self.done = False
        self.surface = None
        self.command = command
        self.messages = messages
        self.log = log
        self.cmd_type = dou_protocol['command']['none']
        self.setting = None
        self.count = 0

    def loop(self, delay):
        if len(self.command) == 0:
            time.sleep(float(delay) / 1000)
            return

        else:
            command = self.command.popleft() 

        if ord(command[0]) == dou_protocol['header']['cmd']:
            self.cmd_type = command[1]
            self.count += 1

        elif ord(command[0]) == dou_protocol['header']['data']:
            try:
                if self.cmd_type == dou_protocol['command']['init']:
                    self.setting = self.get_setting(command[1:])
                    self.surface = pygame.surface.Surface(self.setting['size'])
                    self.messages.append('LCD %08d: Initializtion %s' % (self.count, str(self.setting)))
                    print 'LCD Setting: %s' % str(self.setting)
                    self.log['msg_log']['token'].acquire()
                    self.log['msg_log']['file'].write('LCD %08d: Initializtion %s\n' % (self.count, str(self.setting)))
                    self.log['msg_log']['token'].release()
                
                if self.surface != None:
                    if self.cmd_type == dou_protocol['command']['clear']:
                        color = self.get_color(command[1:], self.setting['byte_per_pixel'])
                        self.surface.fill(color)
                        self.messages.append('LCD %08d: Clear with color %s' % (self.count, str(color)))
                        self.log['msg_log']['token'].acquire()
                        self.log['msg_log']['file'].write('LCD %08d: Clear with color %s\n' % (self.count, str(color)))
                        self.log['msg_log']['token'].release()
                    
                    elif self.cmd_type == dou_protocol['command']['dwPoint']:
                        x, y = self.get_position(command[1:], 2)
                        position = (x, y)
                        color = self.get_color(command[9:], self.setting['byte_per_pixel'])
                        self.surface.set_at(position, color)
                        self.messages.append('LCD %08d: Draw point at %s with color %s' % (self.count, str(position), str(color)))
                        self.log['msg_log']['token'].acquire()
                        self.log['msg_log']['file'].write('LCD %08d: Draw point at %s with color %s\n' % (self.count, str(position), str(color)))
                        self.log['msg_log']['token'].release()
                        
                    elif self.cmd_type == dou_protocol['command']['dwHCLine']:
                        x1, x2, y = self.get_position(command[1:], 3)
                        j = 13
                        temp = []

                        for x in xrange(x1, x2 + 1):
                            position = (x, y)
                            color = self.get_color(command[j:], self.setting['byte_per_pixel'])
                            self.surface.set_at(position, color)
                            j = j + self.setting['byte_per_pixel']
                            temp += '%s ' % str(color)
                        self.messages.append('LCD %08d: Draw horizontal line from %s to %s with colors: %s' % (self.count, str((x1, y)),  str((x2, y)), temp))
                        self.log['msg_log']['token'].acquire()
                        self.log['msg_log']['file'].write('LCD %08d: Draw horizontal line from %s to %s with colors: %s\n' % (self.count, str((x1, y)),  str((x2, y)), temp))
                        self.log['msg_log']['token'].release()
                        
                    elif self.cmd_type == dou_protocol['command']['dwHLine']:
                        x1, x2, y = self.get_position(command[1:], 3)
                        position1 = (x1, y)
                        position2 = (x2, y)
                        color = self.get_color(command[13:], self.setting['byte_per_pixel'])
                        pygame.draw.aaline(self.surface, color, position1, position2)
                        self.messages.append('LCD %08d: Draw horizontal line from %s to %s with color %s' % (self.count, str(position1),  str(position2),  str(color)))
                        self.log['msg_log']['token'].acquire()
                        self.log['msg_log']['file'].write('LCD %08d: Draw horizontal line from %s to %s with color %s\n' % (self.count, str(position1),  str(position2),  str(color)))
                        self.log['msg_log']['token'].release()
                        
                    elif self.cmd_type == dou_protocol['command']['dwVLine']:
                        x, y1, y2 = self.get_position(command[1:], 3)
                        position1 = (x, y1)
                        position2 = (x, y2)
                        color = self.get_color(command[13:], self.setting['byte_per_pixel'])
                        pygame.draw.aaline(self.surface, color, position1, position2)
                        self.messages.append('LCD %08d: Draw vertical line from %s to %s with color %s' % (self.count, str(position1),  str(position2),  str(color)))
                        self.log['msg_log']['token'].acquire()
                        self.log['msg_log']['file'].write('LCD %08d: Draw vertical line from %s to %s with color %s\n' % (self.count, str(position1),  str(position2),  str(color)))
                        self.log['msg_log']['token'].release()
                        
            except (IndexError, OverflowError, TypeError, ValueError) as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]      
                print(exc_type, fname, exc_tb.tb_lineno)

                print 'LCD Error: %s' % str(e)

                to_msg = ''
                for ch in command:
                    to_msg += '%02x' % ord(ch)

                self.messages.append('<LCD Error: %s (%s)>' % (str(e), to_msg))
                self.log['msg_log']['token'].acquire()
                self.log['msg_log']['file'].write('<LCD Error: %s (%s)>\n' % (str(e), to_msg))
                self.log['msg_log']['token'].release()

    def run(self, delay = 10):
        while not self.done:
            self.loop(delay)

        # before exit
        print 'LCD command count: %d\n' % self.count

    def get_setting(self, buffer):
        version = str(ord(buffer[0])) + '.' + str(ord(buffer[1]))
        size = ((ord(buffer[2]) << 8) + (ord(buffer[3])), (ord(buffer[4]) << 8) + (ord(buffer[5])))
        depth = ord(buffer[6])

        if (depth == 24):
            byte_per_pixel = 4

        elif (depth == 16):
            byte_per_pixel = 2

        setting = dict()
        setting['version'] = version
        setting['size'] = size
        setting['depth'] = depth
        setting['byte_per_pixel'] = byte_per_pixel

        return setting

    def get_color(self, buffer, byte_per_pixel):
        c = list()

        if (byte_per_pixel == 4):
            c.append(ord(buffer[2]))
            c.append(ord(buffer[1]))
            c.append(ord(buffer[0]))

        elif (byte_per_pixel == 2):
            c.append(int(round(((ord(buffer[1]) & 0xf8) >> 3) / float(0x1f) * 255)))
            c.append(int(round((((ord(buffer[1]) & 0x07) << 3) + ((ord(buffer[0]) & 0xe0) >> 5)) / float(0x3f) * 255)))
            c.append(int(round((ord(buffer[0]) & 0x1f) / float(0x1f) * 255)))

        return c

    def get_position(self, buffer, number):
        p = list()

        for i in xrange(number):
            p.append(ord(buffer[i * 4]) + (ord(buffer[i * 4 + 1]) << 8) + (ord(buffer[i * 4 + 2]) << 16) + (ord(buffer[i * 4 + 3]) << 24))

        return p






app = App()
app.run(app.widget)

