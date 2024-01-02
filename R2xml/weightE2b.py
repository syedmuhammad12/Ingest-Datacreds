import re
# getting e2b for patient weight
class weightE2b(object):
    
    def weightUnit(self,key,row):
        key = key.lower()
        match = re.match(r'^\d+(?:\.\d+)?',key)
        if match and 'pounds' in key:
            return int(round(float(match.group())) * 0.45359237)
        elif match and 'kg' in key or 'WEIGHT (Kg):' in row.keys():
            return int(match.group())
        elif match:
            return int(round(float(match.group())) * 0.45359237)
        else:    
            return ""