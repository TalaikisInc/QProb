#TODO autointerlinker
#FIXME copied from somewhere, just an example, not implemented

class Autolinker(object):
    ignoreCaseLength = 12
    def __init__(self):
        self.links = {}
        #any item that gets added must have a linkHTML method that accepts a title parameter

    def addItem(self, title, item):
        self.links[title] = item

    def addLinks(self, links):
        for link in links:
            self.links[link.title()] = link

    def replaceAll(self, haystack):
        for title, link in sorted(list(self.links.items()), key=lambda x:-len(x[0])):
            haystack = self.replace(title, link, haystack)
            #we're going paragraph-by-paragraph, but don't want multiple links
            if self.replaced:
                del self.links[title]
        return haystack

    def regexOptions(self, text):
        options = re.DOTALL
        if len(text) > self.ignoreCaseLength:
            options = options | re.IGNORECASE
        return options

    def replace(self, needle, replacement, haystack):
        self.replacement = replacement
        options = self.regexOptions(needle)
        needle = re.compile('([^{}]*?)(' + re.escape(needle) + ')([^{}]*)', options)
        self.needle = needle
        self.replaced = False
        return self.doReplace(haystack)

    def doReplace(self, haystack):
        return re.sub(self.needle, self.matcher, haystack)

    def matcher(self, match):
        fullText = match.group(0)
        if not self.replaced:
            #if it's inside of a django tag, don't make the change
            if fullText[0] == '%' or fullText[-1] == '%':
                return fullText
                #if it's inside of a link already, don't make the change
                leftText = match.group(1)
                matchText = match.group(2)
                rightText = match.group(3)
                rightmostAnchor = leftText.rfind('<a')
                if rightmostAnchor != -1:
                    anchorClose = leftText.rfind('</a>')
                    if anchorClose < rightmostAnchor:
                        #this is inside of an open a tag.
                        #but there might be a match in the rightText
                        fullText = leftText+matchText + self.doReplace(rightText)
                        return fullText
                        #check the right side for anchors, too.
                        leftmostAnchorClose = rightText.find('</a>')
                        if leftmostAnchorClose != -1:
                            anchorOpen = rightText.find('<a')
                            if anchorOpen == -1 or anchorOpen > leftmostAnchorClose:
                                #this is inside of an open a tag
                                return fullText
                                #otherwise, it is safe to make the change
                                fullText = leftText + self.replacement.linkHTML(title=matchText) + rightText
                                self.replaced = True
                                return fullText
