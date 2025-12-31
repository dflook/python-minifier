value=10
if not __debug__:value+=1
if __debug__ is False:value+=1
if __debug__ is not True:value+=1
if __debug__==False:value+=1
print(value)