#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, string, types, exceptions, math 

DEFAULT_TEMPO = 119.99

class midiAnalyzer():
    def __init__(self, path): 
        self.file_path = path
        self.num_track = 0
        self.num_channel = 0
        self.format = 1
        self.tick_per_quarternote = 120
        self.tick_per_second = None
        self.track_name = "no_title"
        self.tempo = DEFAULT_TEMPO
        self.beat_per_bar = 4
        self.base_beat = 4
        self.key = 0
        self.track = [] 
        self.instrument = [] 

    ### WRITE methods
    def setTrackName(self, track_name):
        self.track_name = track_name
        
    def setNumTrack(self, num_track):
        self.num_track = num_track
        
    def setNumChannel(self, num_channel):
        self.num_channel = num_channel
        
    def setTickPerQuarterNote(self, tick_per_second, tick_per_quarternote):
        self.tick_per_second = tick_per_second
        self.tick_per_quarternote = tick_per_quarternote 
        
    def setFormat(self, format):
        self.format = format  
        
    def setTempo(self, tempo):
        if self.tempo == DEFAULT_TEMPO:
            self.tempo = int(tempo) 
         
    def setBeat(self, beat_per_bar, base_beat):
        self.beat_per_bar = beat_per_bar
        self.base_beat = base_beat 
        
    def setKey(self, key):
        self.key = key
         
    def writeMidi(self, midi_event_list, channel_index_list, instrument_index_list):  
        # start write midi
        mf = MidiFile(self) 
        mf.open(self.file_path, "wb") 
        info_track = MidiTrack(0, mf)
        ### 基本信息
        # text event
        text_event = MidiEvent(info_track) 
        text_event.type = "TEXT_EVENT"
        text_event.data = "produced_by_WOYAOXIEGE."
        # track name event
        track_name_event = MidiEvent(info_track) 
        track_name_event.type = "SEQUENCE_TRACK_NAME"
        track_name_event.data = "WOYAOXIEGE"
        # tempo event
        tempo_event = MidiEvent(info_track) 
        tempo_event.type = "SET_TEMPO" 
        MICROSECONDS_PER_MINUTE = 60000000
        MPQN = int(MICROSECONDS_PER_MINUTE / self.tempo)
        tempo_event.data = chr(MPQN / 65536) + chr(MPQN % 65536 / 256) + chr(MPQN % 65536 % 256)
        # Time signiture event
        time_event = MidiEvent(info_track) 
        time_event.type = "TIME_SIGNATURE" 
        time_event.data = chr(self.beat_per_bar) + chr(int(math.log(self.base_beat, 2))) +chr(24) + chr(8)
        # key event
        key_event = MidiEvent(info_track) 
        key_event.type = "KEY_SIGNATURE"
        key_event.data = chr(self.key) + chr(0)
        # delta time event
        delta_t = DeltaTime(info_track) 
        delta_t.time = 0 
        info_track.events.extend([delta_t, text_event, delta_t, track_name_event, delta_t, tempo_event, 
                              delta_t, time_event, delta_t, key_event]) 
        # track end event
        end_event = MidiEvent(info_track)
        end_event.type = "END_OF_TRACK" 
        end_event.data = ""
        info_track.events.extend([delta_t, end_event]) 

        ### 乐器信息
        channel_index_list = [c+1 for c in channel_index_list]
        track_list = []
        for i in xrange(len(channel_index_list)):
            track_list.append(MidiTrack(i+1, mf))  
            program_event = MidiEvent(track_list[i]) 
            program_event.channel = channel_index_list[i]
            program_event.type = "PROGRAM_CHANGE"
            program_event.data = max(0, instrument_index_list[i]) # 防止人声乐器
            # delta time event
            delta_t = DeltaTime(track_list[i]) 
            delta_t.time = 0 
            track_list[i].events.extend([delta_t, program_event]) 
        ### 音符信息
        # PROGRAM change event 
        num_channel = len(channel_index_list)  
        for i in xrange(num_channel):
            note_on_events = []
            note_off_events = []  
            for j in xrange(len(midi_event_list[i])): 
                (midi_pitch, keyDownTime, keyUpTime, vel) = midi_event_list[i][j] 
                # time event
                delta_t_1 = DeltaTime(track_list[i]) 
                delta_t_1.time = keyDownTime # - time
                if midi_pitch == 'E':
                    ## 音高滑轮
                    # note_on event 
                    note_on_event = MidiEvent(track_list[i])
                    note_on_event.type = "PITCH_BEND"
                    note_on_event.channel = channel_index_list[i]
                    note_on_event.pitch = midi_pitch
                    note_on_event.velocity = vel
                    note_on_event.time = keyDownTime # - time
                    # note off event
                    note_off_event = None
                elif midi_pitch == 'B64':
                    ## 64号控制器 （vel=控制器参数0-128 ）
                    # note_on event 
                    note_on_event = MidiEvent(track_list[i])
                    note_on_event.type = "CONTROLLER_CHANGE"
                    note_on_event.channel = channel_index_list[i]
                    note_on_event.pitch = 64
                    note_on_event.velocity = vel
                    note_on_event.time = keyDownTime # - time 
                    # note off event
                    note_off_event = None
                else:
                    ## 音高音符
                    delta_t_2 = DeltaTime(track_list[i]) 
                    delta_t_2.time = keyUpTime #- keyDownTime  
                    # note_on event
                    note_on_event = MidiEvent(track_list[i])
                    note_on_event.type = "NOTE_ON"
                    note_on_event.channel = channel_index_list[i]
                    note_on_event.pitch = midi_pitch
                    note_on_event.velocity = vel
                    note_on_event.time = keyDownTime # - time  
                    # note off event
                    note_off_event = MidiEvent(track_list[i])
                    note_off_event.type = "NOTE_OFF"
                    note_off_event.channel = channel_index_list[i]
                    note_off_event.pitch = midi_pitch
                    note_off_event.velocity = 0 
                    note_off_event.time = keyUpTime 
                # sort & save 
                k = l = -1
                for k in xrange(len(note_on_events) - 1, -1, -1):
                    if keyDownTime >= note_on_events[k][0].time:
                        break
                    if k == 0:
                        k = -1
                note_on_events.insert(k + 1, ([delta_t_1, note_on_event]))

                if note_off_event:
                    for l in xrange(len(note_off_events) - 1, -1, -1): 
                        if keyUpTime >= note_off_events[l][0].time:
                            break
                        if l == 0:
                            l = -1
                    note_off_events.insert(l + 1, ([delta_t_2, note_off_event]))  
            # generate
            m = n = 0
            num_on_event = len(note_on_events)
            num_off_event = len(note_off_events)
            total_time = 0
            while  m != num_on_event or n != num_off_event:
                if m < num_on_event:
                    # in case note_on_event = [no_item_any_more] first
                    on_time = note_on_events[m][0].time 
                    off_time = note_off_events[n][0].time
                    # print m, n, len(note_on_events), len(note_off_events), on_time, off_time
                    if on_time < off_time:
                        # save note_on event
                        note_on_events[m][0].time -= total_time
                        track_list[i].events.extend(note_on_events[m])
                        total_time = on_time
                        m += 1 
                    elif on_time > off_time: 
                        # save note_off event
                        note_off_events[n][0].time -= total_time
                        track_list[i].events.extend(note_off_events[n])
                        total_time = off_time
                        n += 1
                    else: # on_time == off_time: 
                        # save both on & off
                        note_off_events[n][0].time -= total_time
                        total_time = off_time
                        note_on_events[m][0].time -= total_time
                        track_list[i].events.extend(note_off_events[n])
                        track_list[i].events.extend(note_on_events[m])
                        m += 1
                        n += 1
                elif n < num_off_event:
                    # save note_off event
                    off_time = note_off_events[n][0].time
                    note_off_events[n][0].time -= total_time
                    track_list[i].events.extend(note_off_events[n])
                    total_time = off_time
                    n += 1  
            # end event
            end_event = MidiEvent(track_list[i])
            end_event.type = "END_OF_TRACK" 
            end_event.data = ""
            track_list[i].events.extend([delta_t, end_event]) 
        track_list.insert(0, info_track)
        mf.setMidiInfo(self.format, self.tick_per_quarternote, track_list)  
        mf.write() 
        mf.close()  
        
    """ 
    register_note() is a hook that can be overloaded from a script that imports this module. 
    Here is how you might do that, if you wanted to store the notes as tuples in a list. 
    Including the distinction between track and channel offers more flexibility in assigning voices. 
     
                    import midi 
                    notelist = [ ] 
                    def register_note(t, c, p, v, t1, t2): 
                        notelist.append((t, c, p, v, t1, t2)) 
                    midi.register_note = register_note 
    """ 
     
    def register_note(self, track_index, channel_index, pitch, velocity, keyDownTime, keyUpTime): 
        #print track_index, channel_index, pitch, velocity, keyDownTime, keyUpTime
        self.track[track_index][channel_index].append((pitch, keyDownTime, keyUpTime, velocity))
      
    def getTrack(self):
        return self.track
#############SEPERATION################## 
""" 
midi.py -- MIDI classes and parser in Python 
Placed into the public domain in December 2001 by Will Ware  
#
Python MIDI classes: meaningful data structures that represent MIDI events 
and other objects. You can read MIDI files to create such objects, or 
generate a collection of objects and use them to write a MIDI file. 
# 
Helpful MIDI info: 
http://crystal.apana.org.au/ghansper/midi_introduction/midi_file_form... 
http://www.argonet.co.uk/users/lenny/midi/mfile.html 
""" 
 
def showstr(str, n=16): 
    for x in str[:n]: 
        print ('%02x' % ord(x)), 
    print 

def getNumber(str, length): 
    # MIDI uses big-endian for everything 
    sum = 0 
    for i in range(length): 
        sum = (sum << 8) + ord(str[i]) 
    return sum, str[length:] 

def getVariableLengthNumber(str): 
    sum = 0 
    i = 0 
    while 1: 
        x = ord(str[i]) 
        i = i + 1 
        sum = (sum << 7) + (x & 0x7F) 
        if not (x & 0x80): 
            return sum, str[i:] 

def putNumber(num, length): 
    # MIDI uses big-endian for everything 
    lst = [ ] 
    for i in range(length): 
        n = 8 * (length - 1 - i) 
        lst.append(chr((num >> n) & 0xFF)) 
    return string.join(lst, "") 
 
def putVariableLengthNumber(x): 
    lst = [ ] 
    while 1: 
        y, x = x & 0x7F, x >> 7 
        lst.append(chr(y + 0x80)) 
        if x == 0: 
            break 
    lst.reverse() 
    lst[-1] = chr(ord(lst[-1]) & 0x7f) 
    return string.join(lst, "") 


class EnumException(exceptions.Exception): 
    pass 
 
class Enumeration: 
    def __init__(self, enumList): 
        lookup = { } 
        reverseLookup = { } 
        i = 0 
        uniqueNames = [ ] 
        uniqueValues = [ ] 
        for x in enumList: 
            if type(x) == types.TupleType: 
                x, i = x 
            if type(x) != types.StringType: 
                raise EnumException, "enum name is not a string: " + x 
            if type(i) != types.IntType: 
                raise EnumException, "enum value is not an integer: " + i 
            if x in uniqueNames: 
                raise EnumException, "enum name is not unique: " + x 
            if i in uniqueValues: 
                raise EnumException, "enum value is not unique for " + x 
            uniqueNames.append(x) 
            uniqueValues.append(i) 
            lookup[x] = i 
            reverseLookup[i] = x 
            i = i + 1 
        self.lookup = lookup 
        self.reverseLookup = reverseLookup 
    def __add__(self, other): 
        lst = [ ] 
        for k in self.lookup.keys(): 
            lst.append((k, self.lookup[k])) 
        for k in other.lookup.keys(): 
            lst.append((k, other.lookup[k])) 
        return Enumeration(lst) 
    def hasattr(self, attr): 
        return self.lookup.has_key(attr) 
    def has_value(self, attr): 
        return self.reverseLookup.has_key(attr) 
    def __getattr__(self, attr): 
        if not self.lookup.has_key(attr): 
            raise AttributeError 
        return self.lookup[attr] 
    def whatis(self, value): 
        return self.reverseLookup[value] 
 
channelVoiceMessages = Enumeration([("NOTE_OFF", 0x80), 
                                    ("NOTE_ON", 0x90), 
                                    ("POLYPHONIC_KEY_PRESSURE", 0xA0), 
                                    ("CONTROLLER_CHANGE", 0xB0), 
                                    ("PROGRAM_CHANGE", 0xC0), 
                                    ("CHANNEL_KEY_PRESSURE", 0xD0), 
                                    ("PITCH_BEND", 0xE0)]) 
 
channelModeMessages = Enumeration([("ALL_SOUND_OFF", 0x78), 
                                   ("RESET_ALL_CONTROLLERS", 0x79), 
                                   ("LOCAL_CONTROL", 0x7A), 
                                   ("ALL_NOTES_OFF", 0x7B), 
                                   ("OMNI_MODE_OFF", 0x7C), 
                                   ("OMNI_MODE_ON", 0x7D), 
                                   ("MONO_MODE_ON", 0x7E), 
                                   ("POLY_MODE_ON", 0x7F)]) 

metaEvents = Enumeration([("SEQUENCE_NUMBER", 0x00), 
                          ("TEXT_EVENT", 0x01), 
                          ("COPYRIGHT_NOTICE", 0x02), 
                          ("SEQUENCE_TRACK_NAME", 0x03), 
                          ("INSTRUMENT_NAME", 0x04), 
                          ("LYRIC", 0x05), 
                          ("MARKER", 0x06), 
                          ("CUE_POINT", 0x07), 
                          ("MIDI_CHANNEL_PREFIX", 0x20), 
                          ("MIDI_PORT", 0x21), 
                          ("END_OF_TRACK", 0x2F), 
                          ("SET_TEMPO", 0x51), 
                          ("SMTPE_OFFSET", 0x54), 
                          ("TIME_SIGNATURE", 0x58), 
                          ("KEY_SIGNATURE", 0x59), 
                          ("SEQUENCER_SPECIFIC_META_EVENT", 0x7F)]) 
 
# runningStatus appears to want to be an attribute of a MidiTrack. But 
# it doesn't seem to do any harm to implement it as a global. 
runningStatus = None 
 
class MidiEvent: 
 
    def __init__(self, track):  
        self.track = track 
        self.time = None 
        self.channel = self.pitch = self.velocity = self.data = None 
        self.type = None
 
    def __cmp__(self, other): 
        # assert self.time != None and other.time != None  
        return cmp(self.time, other.time) 
 
    def __repr__(self): 
        r = ("<MidiEvent %s, t=%s, track=%s, channel=%s" % 
             (self.type,  repr(self.time),  self.track.index,  repr(self.channel))) 
        for attrib in ["pitch", "data", "velocity"]: 
            if getattr(self, attrib) != None: 
                r = r + ", " + attrib + "=" + repr(getattr(self, attrib)) 
        return r + ">" 
  
    def write(self): 
        sysex_event_dict = {"F0_SYSEX_EVENT": 0xF0, 
                            "F7_SYSEX_EVENT": 0xF7}  
        if channelVoiceMessages.hasattr(self.type): 
            x = chr((self.channel - 1) + getattr(channelVoiceMessages, self.type)) 
            if self.type in ("NOTE_ON", "NOTE_OFF"): 
                self.pitch = max(self.pitch, 0)
                self.velocity = max(self.velocity, 0)  
                data = chr(self.pitch) + chr(self.velocity)  
            elif self.type == "CONTROLLER_CHANGE":
                # 控制器 
                data = chr(self.pitch) + chr(self.velocity)
            elif (self.type != "PROGRAM_CHANGE" and 
                self.type != "CHANNEL_KEY_PRESSURE"):  
                # pitch_bend  音高弯曲的情况： -8192~+8192的情况，转换为0~16384，分为高低位，低位0~127 高位0~127
                self.velocity += 8192
                data = chr(self.velocity%128) + chr(int(self.velocity/128))  
            else: 
                data = chr(self.data) 
            return x + data  
        elif channelModeMessages.hasattr(self.type): 
            x = getattr(channelModeMessages, self.type) 
            x = (chr(0xB0 + (self.channel - 1)) + 
                 chr(x) + 
                 chr(self.data)) 
            return x 
        elif sysex_event_dict.has_key(self.type): 
            str = chr(sysex_event_dict[self.type]) 
            str = str + putVariableLengthNumber(len(self.data)) 
            return str + self.data  
        elif metaEvents.hasattr(self.type): 
            str = chr(0xFF) + chr(getattr(metaEvents, self.type)) 
            str = str + putVariableLengthNumber(len(self.data)) 
            return str + self.data  
        else: 
            raise "unknown midi event type: " + self.type 
 
class MidiChannel:  
    """A channel (together with a track) provides the continuity connecting 
    a NOTE_ON event with its corresponding NOTE_OFF event. Together, those 
    define the beginning and ending times for a Note.""" 
 
    def __init__(self, track, index): 
        self.index = index 
        self.track = track 
        self.pitches = { }  
        
    def __repr__(self): 
        return "<MIDI channel %d>" % self.index  
 
class DeltaTime(MidiEvent):  
    type = "DeltaTime"  
    def read(self, oldstr): 
        self.time, newstr = getVariableLengthNumber(oldstr) 
        return self.time, newstr 
 
    def write(self): 
        str = putVariableLengthNumber(self.time) 
        return str 
 
class MidiTrack:  
    def __init__(self, index, parent):
        self.index = index 
        self.father = parent  
        self.events = [ ] 
        self.channels = [ ] 
        self.length = 0 
        for i in range(16): 
            self.channels.append(MidiChannel(self, i)) 
 
    def read(self, str): 
        time = 0 
        assert str[:4] == "MTrk" 
        length, str = getNumber(str[4:], 4) 
        self.length = length 
        mystr = str[:length] 
        remainder = str[length:] 
        while mystr: 
            # 读取时间事件
            delta_t = DeltaTime(self) 
            dt, mystr = delta_t.read(mystr) 
            time = time + dt 
            self.events.append(delta_t) 
            # 读取音符事件
            e = MidiEvent(self) 
            mystr = e.read(time, mystr) 
            self.events.append(e) 
        return remainder 
 
    def write(self): 
        time = self.events[0].time 
        # build str using MidiEvents 
        str = "" 
        for e in self.events: 
            str = str + e.write() 
        return "MTrk" + putNumber(len(str), 4) + str  
        
    def __repr__(self): 
        r = "<MidiTrack %d -- %d events\n" % (self.index, len(self.events)) 
        for e in self.events: 
            r = r + "    " + `e` + "\n" 
        return r + "  >" 
 
class MidiFile:  
    def __init__(self, parent):
        self.father = parent
        self.file = None 
        self.format = 1 
        self.tracks = [ ] 
        self.ticksPerQuarterNote = None 
        self.ticksPerSecond = None 
 
    def open(self, filename, attrib="rb"): 

        if filename == None: 
            if attrib in ["r", "rb"]: 
                self.file = sys.stdin 
            else: 
                self.file = sys.stdout 
        else:   
            self.file = open(filename, attrib)  
                             
    def __repr__(self): 
        r = "<MidiFile %d tracks\n" % len(self.tracks) 
        for t in self.tracks: 
            r = r + "  " + `t` + "\n" 
        return r + ">" 
 
    def close(self): 
        self.file.close() 
 
    def read(self): 
        return self.readstr(self.file.read()) 
 
    def readstr(self, str):  
        if str[:4] != "MThd" :
            return False 
        length, str = getNumber(str[4:], 4)   
        if length != 6 :
            return False 
        format, str = getNumber(str, 2) 
        self.format = format 
        if format != 0 and format != 1 and format != 2:
            # dunno how to handle 2 
            return False 
        numTracks, str = getNumber(str, 2) 
        division, str = getNumber(str, 2) 
        if division & 0x8000: 
            framesPerSecond = -((division >> 8) | -128) 
            ticksPerFrame = division & 0xFF 
            assert ticksPerFrame == 24 or ticksPerFrame == 25 or \
                   ticksPerFrame == 29 or ticksPerFrame == 30 
            if ticksPerFrame == 29: ticksPerFrame = 30  # drop frame 
            self.ticksPerSecond = ticksPerFrame * framesPerSecond 
        else: 
            self.ticksPerQuarterNote = division & 0x7FFF 
        # save info 
        try:
            self.father.setNumTrack(numTracks)
            self.father.setFormat(self.format)
            self.father.setTickPerQuarterNote(self.ticksPerSecond, self.ticksPerQuarterNote)
            self.father.initMidi() 
        except:
            import traceback
            traceback.print_exc()
        # read each track
        for i in range(numTracks): 
            trk = MidiTrack(i, self.father) 
            str = trk.read(str) 
            self.tracks.append(trk) 
        return True
 
    def setMidiInfo(self, format, tick_per_quarternote, track):
        # for writing midi : 写midi时调用此方法
        self.format = format
        self.tracks = track
        self.ticksPerQuarterNote = tick_per_quarternote
 
    def write(self): 
        self.file.write(self.writestr()) 
 
    def writestr(self): 
        division = self.ticksPerQuarterNote 
        # Don't handle ticksPerSecond yet, too confusing  
        assert (division & 0x8000) == 0 
        str = "MThd" + putNumber(6, 4) + putNumber(self.format, 2) 
        str = str + putNumber(len(self.tracks), 2) 
        str = str + putNumber(division, 2) 
        #print "len(self.tracks) =", len(self.tracks)
        for trk in self.tracks: 
            str = str + trk.write() 
        return str 
  
  
