from binascii import hexlify


def parse_head(data):
    to_return = {'type':'head','filename':'','data':''}
    
    #Parsing filename
    start_offset = 16 #For FileName    
    chr = data[start_offset]
    count = start_offset
    while chr != '20':
        if chr != '00':
            to_return['filename'] += str(bytes.fromhex(chr))[2:3]
        count += 1
        chr = data[count]
    end_offset = count
    
    printer_port = ['3b', '04', '3e', '04', '3a', '04', '3d', 
                    '04', '3e', '04', '42', '04', '00']
    count = end_offset
    chr = data[start_offset]    
    cnt = 0
    found = False
    while True:
        if chr == printer_port[cnt]:                       
            cnt += 1
            if printer_port.index(chr) == len(printer_port)-1:
                found = True
                break
        count += 1
        try:
            chr = data[count]
        except:
            found = False
            break
    if found:
        count += 1
        chr = data[count]
        to_return['port'] = ''
        while chr != '3a':
            if chr != '00':
                to_return['port'] += str(bytes.fromhex(chr))[2:3]
            count += 1
            chr = data[count]
        end_offset = count

    #parse SpecSymbol
    sumb = data[len(data)-32]
    if sumb == 'df':
        to_return['data'] = 'NEW PAGE'
    elif sumb == '18':
        to_return['data'] += '\n'

    return to_return
   
def parse_body(data):
    to_return = {'type':'',
                 'start':0,
                 'end':0,
                 'data':'',
                 'length':0}
    
    if data[0] == '01' :
        to_return['type'] = 'spec'
         
    else:
        to_return['type'] = 'text'    
        #Parse text
        length = int(data[0],16)
        to_return['start'] = 4
        #to_return['length'] = length
        end_offset = 0
        for i in range(4,length):
            if data[i] == '00':
                continue
            if data[i][0] == '1' or data[i][0] == '0':
                break
            
            to_return['data'] += str(bytes.fromhex(data[i]))[2:3]
            end_offset = i
        
        to_return['end'] = end_offset
    
    #parse SpecSumbol
    sumb = data[len(data)-32]#32 - offset of SpecSumbol from the end of block
    if sumb == 'df':
        if to_return['type'] == 'text':
            to_return['data'] += '\n'
        else:
            to_return['data'] = 'NEW PAGE'
    if sumb == '18':
        to_return['data'] += '\n'

    return to_return


class Block:
    def __init__(self,block:list,type:int):
        self.block = block
        if type == 1:
            self.data = parse_head(block)
        else:
            self.data = parse_body(block)
    
    def change(self,new_string:str) -> bool:
        if self.data['type'] == 'spec':
            return False

    
def main_parser(data):
    to_return = []
    block = []
    ff = False
    cnt = 0
    
    for hex in data:

        block.append(hex)
        if cnt == 7:
            if len(to_return) == 0:
                to_return.append(Block(block,1))
            else:
                to_return.append(Block(block,0))
            block = []
            cnt = 0
            ff = False            

        if hex == 'ff':
            cnt += 1
            ff = True
        elif hex != 'ff' and ff:
            cnt = 0
            ff = False

    to_return.append(Block(block,0))  
    return to_return

class SPL:
    def __init__(self,file:str):
        self.file_name = file
        self.spl_file = open(self.file_name,'rb')        
        raw_data = str(hexlify(self.spl_file.read()))[2:-1]
        raw_data = raw_data[0:len(raw_data)]
        self.raw_data = []
        counter = 0
        while counter < len(raw_data):
            self.raw_data.append(raw_data[counter]+raw_data[counter+1])
            counter += 2
        self.blocks = main_parser(self.raw_data)

    def restore_txt(self,output:str):
        file = open(output,'w')
        file.write('Origin FileName(probably):'+self.blocks[0].data['filename']+'\n\n')
        for block in self.blocks[1:]:
            if block.data['data'] != None:
                file.write(block.data['data'])


if __name__ == '__main__':       
    spl = SPL('C:\\Windows\\System32\\spool\\PRINTERS\\FP00009.SPL')
    print(spl.blocks[0].data)
    #file = open('out.txt','wb')
    for block in spl.blocks[1:]:
        if block.data['data'] != None:

            print(block.data['data'])
