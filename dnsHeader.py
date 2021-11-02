
def low(i):
    return i & 0xff
def high(i):
    return (i >> 16) & 0xff

QA = 3
AN = 4
NS = 5
AR = 6

def makeHeader(QA, AN, NS, AR):
    header = 7
    padding = 5 #arbitrary

    out = [(header), ((QA << 16) | AN), ((NS << 16) | AR)]
    byteOut = bytearray([high(header), low(header), high(padding), low(padding), high(QA), low(QA), high(AN), low(AN), 
                        high(NS), low(NS), high(AR), low(AR)])
    outStr = byteOut.decode()

    return outStr

def makeQuestion():
    length = 10
    num = 5
    out = []
    for j in range(5):
        out.append(low(length))
        for i in range(65+j, 65+length+j):
            out.append(low(i))
    out.append(low(0))
    byteOut = bytearray(out)
    print(byteOut)

    return byteOut.decode()

outStr = ""
outStr += makeHeader(QA, AN, NS, AR)
outStr += makeHeader(QA, AN, NS, AR)
outStr += makeHeader(QA, AN, NS, AR)
outStr += makeHeader(QA, AN, NS, AR)
outStr += makeHeader(QA, AN, NS, AR)
outStr += makeHeader(QA, AN, NS, AR)


outStr += "\n"

f = open("dnsHeader.test", "w")
f.write(outStr)
f.close()