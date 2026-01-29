class UnicodeSlugConverter:
    """
    Path converter يقبل slug بالعربي والإنجليزي
    """
    regex = r'[-\w]+'  # \w يشمل Unicode (عربي + إنجليزي)
    
    def to_python(self, value):
        return str(value)
    
    def to_url(self, value):
        return str(value)
