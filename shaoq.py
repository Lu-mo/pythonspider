import requests
from bs4 import BeautifulSoup as bs
import bs4
response = requests.get("http://shaoq.com/ip")
soup = bs(response.text,"lxml")
str = str(soup.head.style)
contents = soup.body.contents
index1 = str.find("{display:none}")
index2 = str.find("{display:none}",index1+1)
name1 = str[index1-4:index1]
name2 = str[index2-4:index2]

with open(r"C:\Users\yxt91\PycharmProjects\pythonspider\shaqIP.html","w",encoding="utf-8") as f:
    f.write(response.text)
    f.flush()

tempstr = ""
for each in contents:
    try:
       #print(each['style'])
       if each['style'] == "display:inline":
           #print(each.text)
           tempstr = tempstr + each.text
           continue
    except:
        try:
            #print(each['class'])
            if each.attrs['class'][0] != name1 and each.attrs['class'][0] != name2:
                #print(each.text)
                tempstr = tempstr + each.text
        except:
            try:
                #print("")
                if each.name == "br":
                    tempstr = tempstr + '\n'
                if type(each) is bs4.element.NavigableString:
                    tempstr = tempstr + "".join(each).replace("\n", "")
            except:
                print("",end="")


print(tempstr)
#print(response.text)