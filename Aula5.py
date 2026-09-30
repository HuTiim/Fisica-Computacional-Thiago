
i = 0


with open('arq.txt','r') as fp:

    linha = fp.readline()

    while linha != '':
        #print(i , linha)
        #i += 1
        linha = fp.readline()