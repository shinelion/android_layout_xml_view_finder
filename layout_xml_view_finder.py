#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Wu Xiaoran (shinelion@qq.com)
import os
import tkinter
import threading
import re
CUSTOM_MEMBER_VAR_DEC_STR = "protected %s %s;"
CUSTOM_FIND_VIEW_STR = "%s = (%s) rootView.findViewById(R.id.%s);"
CUSTOM_SET_CLICK_LISTENER_STR = "%s.setOnClickListener(this);"
SYNTAX_VIEW_ID_DEF = r'\Wandroid:id="@\+id/([\w_]+)"\W'
SYNTAX_VIEW_TYPE_NAME = r'<(?:[\w_]+\.)*([\w_]+)\W'
REGEX_OBJ_VIEW_ID_DEF = re.compile(SYNTAX_VIEW_ID_DEF)
REGEX_OBJ_VIEW_TYPE_NAME = re.compile(SYNTAX_VIEW_TYPE_NAME)
DICT_COMMON_VIEW_TYPE_ABBR = {"Button":"Btn","EditText":"Et","ListView":"Lv","XListView":"Lv","TextView":"Tv","ImageView":"Iv","ViewGroup":"Vg","LinearLayout":"Vg","RelativeLayout":"Vg","AbsoluteLayout":"Vg","FrameLayout":"Vg","AutoAttachRecyclingImageView":"Iv","RoundedImageView":"Iv"}
KNOWN_VIEW_TYPE_NAME_FRAG = ("Btn","Et","View","Lv","Tv","Iv","Vg","Ll","Rl","Layout")
class LayoutXmlViewFinder:
    def processLayoutXml(xmlText):
        NAMING_STYLE_NONE = 0    
        NAMING_STYLE_CAMEL_M = 1   
        NAMING_STYLE_CAMEL = 2
        NAMING_STYLE_TWIKI_WORD = 3
        NAMING_STYLE_UNDERSCORE_LOWER = 4
        NAMING_STYLE_UNDERSCORE_UPPER = 5
        SYNTAX_NAMING_STYLE_CAMEL_M = r'^m([A-Z][a-z0-9]*)([A-Z0-9][a-z0-9]*)*$'
        SYNTAX_NAMING_STYLE_CAMEL = r'^[a-z][a-z0-9]*([A-Z0-9][a-z0-9]*)*$'
        SYNTAX_NAMING_STYLE_TWIKI_WORD = r'^([A-Z][a-z0-9]*)([A-Z0-9][a-z0-9]*)*$'
        SYNTAX_NAMING_STYLE_UNDERSCORE_LOWER = r'^[a-z][a-z0-9]*(_[a-z0-9]+)*$'
        SYNTAX_NAMING_STYLE_UNDERSCORE_UPPER = r'^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$'
        REGEX_OBJ_NAMING_STYLE_CAMEL_M = re.compile(SYNTAX_NAMING_STYLE_CAMEL_M)
        REGEX_OBJ_NAMING_STYLE_CAMEL = re.compile(SYNTAX_NAMING_STYLE_CAMEL)
        REGEX_OBJ_NAMING_STYLE_TWIKI_WORD = re.compile(SYNTAX_NAMING_STYLE_TWIKI_WORD)
        REGEX_OBJ_NAMING_STYLE_UNDERSCORE_LOWER = re.compile(SYNTAX_NAMING_STYLE_UNDERSCORE_LOWER)
        REGEX_OBJ_NAMING_STYLE_UNDERSCORE_UPPER = re.compile(SYNTAX_NAMING_STYLE_UNDERSCORE_UPPER)
        KNOWN_NAMING_STYLE_IDS = (NAMING_STYLE_CAMEL_M, NAMING_STYLE_CAMEL, NAMING_STYLE_TWIKI_WORD, NAMING_STYLE_UNDERSCORE_LOWER, NAMING_STYLE_UNDERSCORE_UPPER)
        KNOWN_NAMING_STYLE_SYNTAXES = (SYNTAX_NAMING_STYLE_CAMEL_M, SYNTAX_NAMING_STYLE_CAMEL, SYNTAX_NAMING_STYLE_TWIKI_WORD, SYNTAX_NAMING_STYLE_UNDERSCORE_LOWER, SYNTAX_NAMING_STYLE_UNDERSCORE_UPPER)
        KNOWN_NAMING_STYLE_REGEX_OBJS = (REGEX_OBJ_NAMING_STYLE_CAMEL_M, REGEX_OBJ_NAMING_STYLE_CAMEL, REGEX_OBJ_NAMING_STYLE_TWIKI_WORD, REGEX_OBJ_NAMING_STYLE_UNDERSCORE_LOWER, REGEX_OBJ_NAMING_STYLE_UNDERSCORE_UPPER)
        VIEW_ID_INFO_IDX = 0
        VIEW_NAME_INFO_IDX = 1
        VIEW_TYPE_INFO_IDX = 2
        def toUppercase(string):
            return string.upper()
        def toLowercase(string):
            return string.lower()
        def toTitlecase(string):
            return string.title()
        def toCamelNaming(string):
            wordIdx = 0
            def transformWord(word):
                nonlocal wordIdx
                ret = word
                if wordIdx > 0:
                    ret = word.title()
                wordIdx += 1
                return ret
            words = detectAndSplitName(string)[1]
            ret = string
            if words:
                ret = "".join(map(transformWord, words))
            return ret
        def toCamelMNaming(string):
            words = detectAndSplitName(string)[1]
            ret = string
            if words:
                ret = "m%s" % ("".join(map(toTitlecase, words)))
            return ret
        def toTwikiWordNaming(string):
            words = detectAndSplitName(string)[1]
            ret = string
            if words:
                ret = ("".join(map(toTitlecase, words)))
            return ret
        def toUnderscoreLowerNaming(string):
            words = detectAndSplitName(string)[1]
            ret = string
            if words:
                ret = "_".join(words)
            return ret
        def toUnderscoreUpperNaming(string):
            words = detectAndSplitName(string)[1] 
            ret = string
            if words:
                ret = "_".join(map(toUppercase, words))
            return ret
        def toCapAbbrNaming(string):
            words = detectAndSplitName(string)[1] 
            ret = string
            if words:
                ret = "".join(map(lambda x: x[0:1].lower(), words))
            return ret
        def toCapAbbrFirstUpperNaming(string):
            return toCapAbbrNaming(string).title()
        def splitName(string):
            return detectAndSplitName(string)[1]
        def detectAndSplitName(string):
            def splitCamelMStyleName(string):
                words = []
                wordStart = 1
                for i in range(2, len(string)):
                    if string[i].isupper() and wordStart < i:
                        words.append(string[wordStart : i].lower())
                        wordStart = i
                words.append(string[wordStart:].lower())
                return words
            def splitCamelStyleName(string):
                words = []
                wordStart = 0
                for i in range(1, len(string)):
                    if string[i].isupper() and wordStart < i:
                        words.append(string[wordStart : i].lower())
                        wordStart = i
                words.append(string[wordStart:].lower())
                return words
            def splitTwikiWordNameStyleName(string):
                words = []
                wordStart = 0
                for i in range(1, len(string)):
                    if string[i].isupper() and wordStart < i:
                        words.append(string[wordStart : i].lower())
                        wordStart = i
                words.append(string[wordStart:].lower())
                return words
            def splitUnderscoreStyleName(string):
                ret = (string)
                if string:
                    ret = list(map(toLowercase, string.split('_')))
                return ret
            style = detectNamingStyle(string)
            result = (style, None)
            if style == NAMING_STYLE_CAMEL_M:
                result = (style, splitCamelMStyleName(string))
            elif style == NAMING_STYLE_CAMEL:
                result = (style, splitCamelStyleName(string))
            elif style == NAMING_STYLE_TWIKI_WORD:
                result = (style, splitTwikiWordNameStyleName(string))
            elif style == NAMING_STYLE_UNDERSCORE_LOWER or style == NAMING_STYLE_UNDERSCORE_UPPER:
                result = (style, splitUnderscoreStyleName(string))
            return result
        def detectNamingStyle(string):
            style = NAMING_STYLE_NONE
            for i in range(len(KNOWN_NAMING_STYLE_REGEX_OBJS)):
                regexObj = KNOWN_NAMING_STYLE_REGEX_OBJS[i]
                if regexObj.match(string):
                    style = KNOWN_NAMING_STYLE_IDS[i]
                    break
            return style
        def delXmlComments(xmlText):
            pass
        def findAllViewIdLocations(xmlText):
            viewIdLocations = []
            viewIdList = []
            for m in REGEX_OBJ_VIEW_ID_DEF.finditer(xmlText):
                viewIdLocations.append(m.start(1))
                viewIdList.append(m.group(1))
            return viewIdList, viewIdLocations
        def findAllViewTypes(xmlText, viewIdLocations):
            viewTypeList = []
            for idLocation in viewIdLocations:
                viewTypeStartLocation = xmlText.rfind("<", 0, idLocation)
                m = REGEX_OBJ_VIEW_TYPE_NAME.search(xmlText, viewTypeStartLocation)
                if m:
                    viewTypeList.append(m.group(1))
                else:
                    print("m is None. viewTypeStartLocation = %d" %(viewTypeStartLocation))
            return viewTypeList
        def translateToViewName(viewIdList, viewTypeList):
            viewNameList = []
            for i in range(len(viewIdList)):
                viewName = toCamelMNaming(viewIdList[i])
#                if not viewNameContainsViewType(viewName, viewTypeList[i]) :
#                    if viewTypeList[i] in DICT_COMMON_VIEW_TYPE_ABBR: 
#                        nameSuffix = DICT_COMMON_VIEW_TYPE_ABBR[viewTypeList[i]]
#                    else:
#                        nameSuffix = toCapAbbrFirstUpperNaming(viewTypeList[i])
#                    viewName += nameSuffix
                viewNameList.append(viewName)
            return viewNameList
        def viewNameContainsViewType(viewName, viewTypeName):
            viewTypeNameAbbr = toCapAbbrFirstUpperNaming(viewTypeName)
            if viewTypeName in DICT_COMMON_VIEW_TYPE_ABBR: 
                nameSuffix = DICT_COMMON_VIEW_TYPE_ABBR[viewTypeName]
            else:
                nameSuffix = toCapAbbrFirstUpperNaming(viewTypeName)
            ret = (viewName[1:].startswith(nameSuffix)
                    or viewName.endswith(nameSuffix)
                    or viewName[1:].startswith(viewTypeNameAbbr)
                    or viewName.endswith(viewTypeNameAbbr)
                    or viewName[1:].startswith(viewTypeName)
                    or viewName.endswith(viewTypeName))
            if not ret:
                for viewTypeFrag in KNOWN_VIEW_TYPE_NAME_FRAG:
                    if viewName[1:].startswith(viewTypeFrag) \
                        or viewName.endswith(viewTypeFrag):
                        ret = True
                        break
            return ret
        def genRelatedSrcForViewList(viewInfoList):
            outputParts = []
            outputParts.append(genViewDeclForList(viewInfoList))
            outputParts.append(genViewVarAssignmentForList(viewInfoList))
            outputParts.append(genViewClickBindingForList(viewInfoList))
            outputParts.append(genViewIdSwitchCaseForList(viewInfoList))
            return ("\n" * 4).join(outputParts)
        def genViewDeclForList(viewInfoList):
            outputParts = []
            for viewInfo in viewInfoList:
                outputParts.append(CUSTOM_MEMBER_VAR_DEC_STR %(viewInfo[VIEW_TYPE_INFO_IDX], viewInfo[VIEW_NAME_INFO_IDX]))
            return "\n".join(outputParts)
        def genViewVarAssignmentForList(viewInfoList):
            outputParts = []
            for viewInfo in viewInfoList:
                outputParts.append(CUSTOM_FIND_VIEW_STR %(viewInfo[VIEW_NAME_INFO_IDX], viewInfo[VIEW_TYPE_INFO_IDX], viewInfo[VIEW_ID_INFO_IDX]))
            print(list(viewInfoList))
            return "\n".join(outputParts)
        def genViewClickBindingForList(viewInfoList):
            outputParts = []
            for viewInfo in viewInfoList:
                outputParts.append(CUSTOM_SET_CLICK_LISTENER_STR %(viewInfo[VIEW_NAME_INFO_IDX]))
            return "\n".join(outputParts)
        def genViewIdSwitchCaseForList(viewInfoList):
            outputParts = []
            outputParts.append("switch (id) {")
            for viewInfo in viewInfoList:
                outputParts.append("    case R.id.%s: {\n        break;\n    }" %(viewInfo[VIEW_ID_INFO_IDX]))
            outputParts.append("}")
            return "\n".join(outputParts)
        viewIdList, viewIdLocations = findAllViewIdLocations(xmlText)
        viewTypeList = findAllViewTypes(xmlText, viewIdLocations)
        viewNameList = translateToViewName(viewIdList, viewTypeList)
        viewInfoList = list(zip(viewIdList, viewNameList, viewTypeList))
        print(viewIdList)
        print(viewTypeList)
        print(viewNameList)
        return genRelatedSrcForViewList(viewInfoList)
    def delLastLineSep(string):
        if string.endswith(os.linesep):
            return string[:-1]
        else:
            return string
class LayoutXmlViewFinderUi:
    uiTitle = "LayoutXmlViewFinderUi"
    gettingTextDelay = 1
    inputtingDelay = 1
    def __init__(self):
        self.timer = None
    def onInputTextChanged(self, e):
        if self.timer :
            self.timer.cancel()
        print("LayoutXmlViewFinderUi:onInputTextChanged :: %s" %(e.char.encode('Latin-1')))
        if e.char == "\x16" :
            self.timer = threading.Timer(self.gettingTextDelay, self.goProcessingInputs)
            self.timer.start()
        else :
            self.timer = threading.Timer(self.inputtingDelay, self.goProcessingInputs)
            self.timer.start()
    def clearOutputText(self):
        print("LayoutXmlViewFinderUi:clearOutputText")
        if self.viewOutputText:
            self.viewOutputText.delete(1.0, tkinter.END)
    def updateViewOutputText(self, outputText):
        print("LayoutXmlViewFinderUi:updateViewOutputText")
        if self.viewOutputText:
            self.viewOutputText.delete(1.0, tkinter.END)
            self.viewOutputText.insert(1.0, outputText)
    def goProcessingInputs(self):
        print("LayoutXmlViewFinderUi:goProcessingInputs")
        self.clearOutputText()
        if self.viewInputText :
            inputText = LayoutXmlViewFinder.delLastLineSep(self.viewInputText.get(1.0, tkinter.END))
        self.resultText = LayoutXmlViewFinder.processLayoutXml(inputText)
        self.updateViewOutputText(self.resultText)
    def showUi(self):
        self.viewRoot = tkinter.Tk() 
        self.viewRoot.title(self.uiTitle)
        main_frame = tkinter.Frame(self.viewRoot)
        main_frame.pack(side=tkinter.BOTTOM)
        self.viewInputText = tkinter.Text(main_frame, width=80, height=60)
        self.viewInputText.bind("<KeyPress>", lambda e: self.onInputTextChanged(e))
        self.viewInputText.pack(side=tkinter.LEFT)
        self.viewOutputText = tkinter.Text(main_frame, width=80, height=60)
        self.viewOutputText.pack(side=tkinter.RIGHT)
        self.viewRoot.mainloop() 
if __name__ == "__main__":
    ui = LayoutXmlViewFinderUi()
    ui.showUi()
