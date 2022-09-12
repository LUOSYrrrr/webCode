import jieba
import jieba.posseg as pseg
import re
from string import punctuation

def clear(s1):
    add_punc = '」|!-——……#，。、【】“”：；（）《》‘’{}？！⑦()%^<>℃^￥‎ '
    punc=punctuation+add_punc
    s2 = ''
    for ch in s1:
        if ch not in punc:
            s2 += ch
    s3=re.sub('\s+','',s2)
    return s3

class Ner():
    def __init__(self):
        jieba.enable_paddle()
        # 正则
        self.tele = r'(?:(?:\+|00)86)?1[3-9]\d{9}'
        # self.tele2 = r'(?:(?:\d{3}-)?\d{8}|^(?:\d{4}-)?\d{7,8})(?:-\d+)?'  # 座机,容易匹配到tg号的一部分
        self.url = r'http[s]?://(?:[a-zA-Z]|[0-9]){1,10}\.(?:[a-zA-Z]|[0-9]|[_/.&+?\\]|(?:%[0-9a-fA-F][0-9a-fA-F])){1,30}'
        self.car = r'[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-HJ-NP-Z][A-HJ-NP-Z0-9]{4,5}[A-HJ-NP-Z0-9挂学警港澳]'
        self.email = r'(?:\w{1,20})@(?:\w{1,5})\.(?:\w{1,5})'
        self.id = r'[1-9]\d{5}(?:18|19|20)\d{2}(?:0[1-9]|10|11|12)(?:0[1-9]|[1-2]\d|30|31)\d{3}[\dXx]'
        self.qq = r'(?:[Qq企鹅]{1,3})(?:[:：\s]{1,2})[1-9][0-9]{4,10}'
        self.wx = r'(?:[vxwVXW微信薇]{1,3})(?:[:：\s]{1,2})(?:[a-zA-Z][-_a-zA-Z0-9]{5,19})'
        self.tg = r'@(?:[0-9a-zA-Z]{5,15})'
        self.bat = r'(?:蝙蝠|蝙蝠ID|batID)(?:[:：\s]{0,2})(?:\d{5,15})'

    # return set
    def plot(self, text):
        words = pseg.cut(text, use_paddle=True)
        per, loc, org, time = [], [], [], []
        for word, tag in words:
            word=clear(word)
            if(len(word)>1):
                if (tag == 'nr' or tag == 'PER'):
                    per.append(word)
                elif (tag == 'ns' or tag == 'LOC'):
                    loc.append(word)
                elif (tag == 'nt' or tag == 'ORG'):
                    org.append(word)
                elif (tag == 't' or tag == 'TIME'):
                    time.append(word)
        return set(per), set(loc), set(org), set(time)

    # return set
    def contact(self, text):
        strs = [self.tele, self.url, self.car, self.email, self.id, self.qq, self.wx, self.tg, self.bat]
        info = set()
        for s in strs:
            temp = set(re.findall(s, text, re.A))
            info = info | temp

        return info
