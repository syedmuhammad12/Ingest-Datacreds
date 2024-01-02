import re
# getting e2b for patient height
class heightE2b(object):
    
    def heightUnit(self,key):
        key = key.lower()
        match = re.match(r'^\d+(?:\.\d+)?',key)
        if match and 'inches' in key:
            return int(round(float(match.group())) * 2.54)
        elif match:
            return int(round(float(match.group())) * 2.54)
        else:    
            return ""
        